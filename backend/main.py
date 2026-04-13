from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import datetime
from pydantic import BaseModel

from . import models, scryfall_client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./mtg_collection.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
client = scryfall_client.ScryfallClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class CardAdd(BaseModel):
    oracle_id: str
    name: str

class CardRemove(BaseModel):
    oracle_id: str

class TagAdd(BaseModel):
    tag_name: str

class DeckCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DeckCardAdd(BaseModel):
    oracle_id: str
    category: str = "Main"

class DeckCardRemove(BaseModel):
    oracle_id: str
    category: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/cards/autocomplete")
def autocomplete(q: str):
    return client.autocomplete(q)

@app.get("/cards/search")
def search_cards(q: str, lang: Optional[str] = None):
    return client.search_cards(q, lang)

@app.get("/collection")
def get_collection(
    db: Session = Depends(get_db),
    color: Optional[str] = None,
    type: Optional[str] = None,
    format: Optional[str] = None,
    keyword: Optional[str] = None,
    set_code: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    query = db.query(models.CollectionCard)
    if color:
        query = query.filter(models.CollectionCard.color_identity.contains([color.upper()]))
    if type:
        query = query.filter(models.CollectionCard.type_line.ilike(f"%{type}%"))
    if min_price is not None:
        query = query.filter(models.CollectionCard.price_eur >= min_price)
    if max_price is not None:
        query = query.filter(models.CollectionCard.price_eur <= max_price)

    cards = query.all()
    result = []
    for card in cards:
        if keyword and keyword.lower() not in [k.lower() for k in (card.keywords or [])]:
            continue
        if format and (card.legalities or {}).get(format) != "legal":
            continue
        if set_code:
            set_printings = client.search_cards(f"oracle_id:{card.oracle_id} set:{set_code}")
            if not set_printings:
                continue

        decks = [dc.deck.name for dc in card.deck_cards]
        result.append({
            "oracle_id": card.oracle_id,
            "name": card.name,
            "quantity": card.quantity,
            "details": {
                "type_line": card.type_line,
                "mana_cost": card.mana_cost,
                "oracle_text": card.oracle_text,
                "image_uris": {"normal": card.image_url},
                "prices": {"eur": str(card.price_eur)},
                "color_identity": card.color_identity,
                "legalities": card.legalities,
                "keywords": card.keywords
            },
            "decks": list(set(decks)),
            "tags": [t.name for t in card.tags]
        })
    return result

@app.post("/collection/add")
def add_to_collection(card_in: CardAdd, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == card_in.oracle_id).first()
    if card:
        card.quantity += 1
    else:
        details = client.get_card_details(card_in.oracle_id)
        if not details:
            raise HTTPException(status_code=404, detail="Scryfall data not found")
        price = client.get_cheapest_price(card_in.oracle_id)
        card = models.CollectionCard(
            oracle_id=card_in.oracle_id,
            name=card_in.name,
            quantity=1,
            type_line=details.get("type_line"),
            mana_cost=details.get("mana_cost"),
            cmc=details.get("cmc"),
            oracle_text=details.get("oracle_text"),
            color_identity=details.get("color_identity"),
            image_url=details.get("image_uris", {}).get("normal"),
            price_eur=price,
            legalities=details.get("legalities"),
            keywords=details.get("keywords")
        )
        db.add(card)
    db.commit()
    return {"status": "success", "quantity": card.quantity}

@app.post("/collection/remove")
def remove_from_collection(card_in: CardRemove, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == card_in.oracle_id).first()
    if card:
        if card.quantity > 1:
            card.quantity -= 1
        else:
            db.delete(card)
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Not found")

@app.post("/collection/{oracle_id}/tags")
def add_tag(oracle_id: str, tag_in: TagAdd, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == oracle_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    tag = db.query(models.Tag).filter(models.Tag.name == tag_in.tag_name).first()
    if not tag:
        tag = models.Tag(name=tag_in.tag_name)
        db.add(tag)
        db.flush()
    if tag not in card.tags:
        card.tags.append(tag)
        db.commit()
    return {"status": "success"}

@app.delete("/collection/{oracle_id}/tags/{tag_name}")
def remove_tag(oracle_id: str, tag_name: str, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == oracle_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if tag and tag in card.tags:
        card.tags.remove(tag)
        db.commit()
    return {"status": "success"}

@app.get("/decks")
def get_decks(db: Session = Depends(get_db)):
    return db.query(models.Deck).all()

@app.post("/decks")
def create_deck(deck_in: DeckCreate, db: Session = Depends(get_db)):
    deck = models.Deck(name=deck_in.name, description=deck_in.description)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck

@app.get("/decks/{deck_id}")
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Not found")
    cards = []
    for dc in deck.cards:
        cards.append({
            "oracle_id": dc.oracle_id,
            "name": dc.card.name,
            "quantity": dc.quantity,
            "category": dc.category,
            "details": {
                "type_line": dc.card.type_line,
                "mana_cost": dc.card.mana_cost,
                "oracle_text": dc.card.oracle_text,
                "image_uris": {"normal": dc.card.image_url},
                "prices": {"eur": str(dc.card.price_eur)},
                "color_identity": dc.card.color_identity
            }
        })
    return {"id": deck.id, "name": deck.name, "description": deck.description, "cards": cards}

@app.post("/decks/{deck_id}/add")
def add_card_to_deck(deck_id: int, card_in: DeckCardAdd, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == card_in.oracle_id).first()
    if not card: raise HTTPException(status_code=404, detail="Add to collection first")
    deck_card = db.query(models.DeckCard).filter(models.DeckCard.deck_id == deck_id, models.DeckCard.oracle_id == card_in.oracle_id, models.DeckCard.category == card_in.category).first()
    if deck_card: deck_card.quantity += 1
    else:
        deck_card = models.DeckCard(deck_id=deck_id, oracle_id=card_in.oracle_id, quantity=1, category=card_in.category)
        db.add(deck_card)
    db.commit()
    return {"status": "success"}

@app.post("/decks/{deck_id}/remove")
def remove_card_from_deck(deck_id: int, card_in: DeckCardRemove, db: Session = Depends(get_db)):
    deck_card = db.query(models.DeckCard).filter(models.DeckCard.deck_id == deck_id, models.DeckCard.oracle_id == card_in.oracle_id, models.DeckCard.category == card_in.category).first()
    if deck_card:
        if deck_card.quantity > 1: deck_card.quantity -= 1
        else: db.delete(deck_card)
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404)

@app.get("/stats/value")
def get_collection_value(db: Session = Depends(get_db)):
    cards = db.query(models.CollectionCard).all()
    total_value = sum((card.price_eur or 0) * card.quantity for card in cards if (card.price_eur or 0) > 1.0)
    last_history = db.query(models.ValueHistory).order_by(models.ValueHistory.timestamp.desc()).first()
    if not last_history or (datetime.datetime.utcnow() - last_history.timestamp).total_seconds() > 3600:
        db.add(models.ValueHistory(total_value=total_value))
        db.commit()
    history_data = db.query(models.ValueHistory).order_by(models.ValueHistory.timestamp).all()
    return {"total_value": total_value, "history": [{"timestamp": h.timestamp, "value": h.total_value} for h in history_data]}
