from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import datetime
from pydantic import BaseModel
import re

try:
    from . import models, scryfall_client
except ImportError:
    import models, scryfall_client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./mtg_user_data.db"
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

class DeckRename(BaseModel):
    name: str

class BulkImport(BaseModel):
    deck_id: Optional[int] = None
    list_text: str

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

def _save_to_api_cache(db: Session, key: str, data: Any):
    cached = db.query(models.APICache).filter(models.APICache.query_key == key).first()
    if cached:
        cached.response_json = data
        cached.timestamp = datetime.datetime.utcnow()
    else:
        db.add(models.APICache(query_key=key, response_json=data))

@app.get("/cards/autocomplete")
def autocomplete(q: str, db: Session = Depends(get_db)):
    cache_key = f"autocomplete:{q}"
    cached = db.query(models.APICache).filter(models.APICache.query_key == cache_key).first()
    if cached and (datetime.datetime.utcnow() - cached.timestamp).total_seconds() < 86400:
        return cached.response_json

    res = client.autocomplete(q)
    _save_to_api_cache(db, cache_key, res)
    db.commit()
    return res

@app.get("/cards/search")
def search_cards(q: str, lang: Optional[str] = None, exact: bool = False, db: Session = Depends(get_db)):
    cache_key = f"search:{q}:{lang}:{exact}"
    cached = db.query(models.APICache).filter(models.APICache.query_key == cache_key).first()
    if cached and (datetime.datetime.utcnow() - cached.timestamp).total_seconds() < 86400:
        return cached.response_json

    res = client.search_cards(q, lang, exact)
    _save_to_api_cache(db, cache_key, res)
    db.commit()
    return res

@app.get("/collection")
def get_collection(
    db: Session = Depends(get_db),
    colors: Optional[str] = None,
    color_identity: Optional[str] = None,
    type: Optional[str] = None,
    format: Optional[str] = None,
    keyword: Optional[str] = None,
    set_code: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tag: Optional[str] = None,
    include_zero: bool = False,
    limit: int = 20,
    offset: int = 0
):
    query = db.query(models.CollectionCard)
    if not include_zero:
        query = query.filter(models.CollectionCard.quantity > 0)
    if type:
        query = query.filter(models.CollectionCard.type_line.ilike(f"%{type}%"))
    if min_price is not None:
        query = query.filter(models.CollectionCard.price_eur >= min_price)
    if max_price is not None:
        query = query.filter(models.CollectionCard.price_eur <= max_price)

    if set_code:
        # Optimization: Fetch all oracle_ids for this set first
        cache_key = f"set_oracle_ids:{set_code}"
        cached = db.query(models.APICache).filter(models.APICache.query_key == cache_key).first()
        if cached and (datetime.datetime.utcnow() - cached.timestamp).total_seconds() < 86400:
            set_oracle_ids = set(cached.response_json)
        else:
            res = client.search_cards(f"set:{set_code}")
            set_oracle_ids = {c['oracle_id'] for c in res if 'oracle_id' in c}
            _save_to_api_cache(db, cache_key, list(set_oracle_ids))
            db.commit()
        query = query.filter(models.CollectionCard.oracle_id.in_(list(set_oracle_ids)))

    all_cards = query.all()
    filtered_cards = []
    for card in all_cards:
        if colors:
            target_colors = set(c.upper() for c in colors.split(","))
            card_colors = set(card.colors or [])
            if not card_colors.issubset(target_colors): continue
        if color_identity:
            target_id = set(c.upper() for c in color_identity.split(","))
            card_id = set(card.color_identity or [])
            if not card_id.issubset(target_id): continue
        if tag:
            if tag.lower() not in [t.name.lower() for t in card.tags]: continue
        if keyword and keyword.lower() not in [k.lower() for k in (card.keywords or [])]: continue
        if format and (card.legalities or {}).get(format) != "legal": continue

        decks = [dc.deck.name for dc in card.deck_cards]
        filtered_cards.append({
            "oracle_id": card.oracle_id,
            "name": card.name,
            "quantity": card.quantity,
            "details": {
                "type_line": card.type_line,
                "mana_cost": card.mana_cost,
                "oracle_text": card.oracle_text,
                "power": card.power,
                "toughness": card.toughness,
                "loyalty": card.loyalty,
                "image_uris": {"normal": card.image_url},
                "prices": {"eur": str(card.price_eur)},
                "colors": card.colors,
                "color_identity": card.color_identity,
                "legalities": card.legalities,
                "keywords": card.keywords
            },
            "decks": list(set(decks)),
            "tags": [t.name for t in card.tags]
        })

    paginated = filtered_cards[offset:offset+limit]
    return {"items": paginated, "total": len(filtered_cards), "has_more": offset + limit < len(filtered_cards)}

def _add_to_collection_internal(oracle_id: str, name: str, db: Session, quantity: int = 1, card_data: Dict = None):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == oracle_id).first()
    if card:
        card.quantity += quantity
    else:
        details = card_data or client.get_card_details(oracle_id)
        if not details: return None
        # Handle if details is from a search result which might have different keys
        prices = details.get("prices", {})
        eur_price = prices.get("eur") or prices.get("eur_foil")
        price = float(eur_price) if eur_price else 0.0

        card = models.CollectionCard(
            oracle_id=oracle_id, name=name, quantity=quantity,
            type_line=details.get("type_line"), mana_cost=details.get("mana_cost"),
            cmc=details.get("cmc"), oracle_text=details.get("oracle_text"),
            power=details.get("power"), toughness=details.get("toughness"),
            loyalty=details.get("loyalty"), colors=details.get("colors"),
            color_identity=details.get("color_identity"),
            image_url=details.get("image_uris", {}).get("normal"),
            price_eur=price, legalities=details.get("legalities"),
            keywords=details.get("keywords")
        )
        db.add(card)
    return card

@app.post("/collection/add")
def add_to_collection(card_in: CardAdd, db: Session = Depends(get_db)):
    card = _add_to_collection_internal(card_in.oracle_id, card_in.name, db)
    if not card: raise HTTPException(status_code=404)
    db.commit()
    return {"status": "success", "quantity": card.quantity}

@app.post("/collection/remove")
def remove_from_collection(card_in: CardRemove, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == card_in.oracle_id).first()
    if card:
        if card.quantity > 0: card.quantity -= 1
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404)

@app.post("/bulk_import")
def bulk_import(import_in: BulkImport, db: Session = Depends(get_db)):
    lines = import_in.list_text.strip().split('\n')

    # Pre-parse lines
    parsed_items = []
    for line in lines:
        line = line.strip()
        if not line: continue
        # Regex to handle: "4 Lightning Bolt", "4x Lightning Bolt", "1 Counterspell (ELD) 22"
        match = re.match(r'^(\d+)x?\s+([^(]+)(?:\s+\(([^)]+)\))?(?:\s+(\d+))?.*$', line)
        if match:
            qty = int(match.group(1))
            name = match.group(2).strip()
            # Clean up trailing numbers if name wasn't perfectly parsed
            name = re.sub(r'\s+\d+.*$', '', name).strip()
            set_code = match.group(3)
            collector_number = match.group(4)
            parsed_items.append({"qty": qty, "name": name, "set": set_code, "cn": collector_number})

    if not parsed_items:
        return {"status": "success", "added": 0}

    # Identify what we already have in DB or Cache
    to_fetch = []
    results_map = {} # oracle_id -> card_data

    for item in parsed_items:
        name = item['name']
        existing = db.query(models.CollectionCard).filter(models.CollectionCard.name.ilike(name)).first()
        if existing:
            item['oracle_id'] = existing.oracle_id
            item['resolved_name'] = existing.name
            continue

        # Check cache
        cache_key = f"search:{name}:None:True"
        cached = db.query(models.APICache).filter(models.APICache.query_key == cache_key).first()
        if cached and (datetime.datetime.utcnow() - cached.timestamp).total_seconds() < 86400:
            search_res = cached.response_json
            if search_res:
                item['oracle_id'] = search_res[0]['oracle_id']
                item['resolved_name'] = search_res[0]['name']
                results_map[item['oracle_id']] = search_res[0]
                continue

        # Need to fetch from Scryfall
        to_fetch.append(item)

    # Batch fetch from Scryfall
    if to_fetch:
        for i in range(0, len(to_fetch), 75):
            batch = to_fetch[i:i+75]
            identifiers = []
            for b in batch:
                if b['set'] and b['cn']:
                    identifiers.append({"set": b['set'], "collector_number": b['cn']})
                else:
                    identifiers.append({"name": b['name']})

            scry_results = client.get_collection_batch(identifiers)
            for idx, res in enumerate(scry_results):
                if res.get("oracle_id"):
                    oracle_id = res['oracle_id']
                    name = res['name']
                    # Map back to original item
                    batch[idx]['oracle_id'] = oracle_id
                    batch[idx]['resolved_name'] = name
                    results_map[oracle_id] = res
                    # Save to cache
                    _save_to_api_cache(db, f"search:{batch[idx]['name']}:None:True", [res])

    # Now add all to collection
    added_count = 0
    for item in parsed_items:
        if 'oracle_id' in item:
            card_data = results_map.get(item['oracle_id'])
            _add_to_collection_internal(item['oracle_id'], item['resolved_name'], db, item['qty'], card_data)

            if import_in.deck_id:
                dc = db.query(models.DeckCard).filter(
                    models.DeckCard.deck_id == import_in.deck_id,
                    models.DeckCard.oracle_id == item['oracle_id'],
                    models.DeckCard.category == "Main"
                ).first()
                if dc:
                    dc.quantity += item['qty']
                else:
                    db.add(models.DeckCard(
                        deck_id=import_in.deck_id,
                        oracle_id=item['oracle_id'],
                        quantity=item['qty'],
                        category="Main"
                    ))
            added_count += 1

    db.commit()
    return {"status": "success", "added": added_count}

@app.post("/collection/{oracle_id}/tags")
def add_tag(oracle_id: str, tag_in: TagAdd, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == oracle_id).first()
    if not card: raise HTTPException(status_code=404)
    tag = db.query(models.Tag).filter(models.Tag.name == tag_in.tag_name).first()
    if not tag:
        tag = models.Tag(name=tag_in.tag_name)
        db.add(tag); db.flush()
    if tag not in card.tags: card.tags.append(tag); db.commit()
    return {"status": "success"}

@app.delete("/collection/{oracle_id}/tags/{tag_name}")
def remove_tag(oracle_id: str, tag_name: str, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == oracle_id).first()
    if not card: raise HTTPException(status_code=404)
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if tag and tag in card.tags: card.tags.remove(tag); db.commit()
    return {"status": "success"}

@app.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    return [t.name for t in db.query(models.Tag).all()]

@app.get("/decks")
def get_decks(db: Session = Depends(get_db)):
    return db.query(models.Deck).all()

@app.post("/decks")
def create_deck(deck_in: DeckCreate, db: Session = Depends(get_db)):
    deck = models.Deck(name=deck_in.name, description=deck_in.description)
    db.add(deck); db.commit(); db.refresh(deck)
    return deck

@app.delete("/decks/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck: raise HTTPException(status_code=404)
    db.query(models.DeckCard).filter(models.DeckCard.deck_id == deck_id).delete()
    db.delete(deck); db.commit()
    return {"status": "success"}

@app.patch("/decks/{deck_id}")
def rename_deck(deck_id: int, rename_in: DeckRename, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck: raise HTTPException(status_code=404)
    deck.name = rename_in.name
    db.commit(); db.refresh(deck)
    return deck

@app.post("/decks/{deck_id}/clone")
def clone_deck(deck_id: int, db: Session = Depends(get_db)):
    original = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not original: raise HTTPException(status_code=404)
    cloned = models.Deck(name=f"Copy of {original.name}", description=original.description)
    db.add(cloned); db.flush()
    for card in original.cards:
        db.add(models.DeckCard(deck_id=cloned.id, oracle_id=card.oracle_id, quantity=card.quantity, category=card.category))
    db.commit(); db.refresh(cloned)
    return cloned

@app.get("/decks/{deck_id}")
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck: raise HTTPException(status_code=404)
    cards = []
    for dc in deck.cards:
        if not dc.card:
            details = client.get_card_details(dc.oracle_id)
            if details:
                 _add_to_collection_internal(dc.oracle_id, details['name'], db, 0, details)
                 db.commit(); db.refresh(dc)

        if dc.card:
            other_decks = [d.deck.name for d in dc.card.deck_cards]
            cards.append({
                "oracle_id": dc.oracle_id, "name": dc.card.name, "quantity": dc.quantity, "category": dc.category,
                "decks": list(set(other_decks)),
                "tags": [t.name for t in dc.card.tags],
                "details": {
                    "type_line": dc.card.type_line, "mana_cost": dc.card.mana_cost, "oracle_text": dc.card.oracle_text,
                    "power": dc.card.power, "toughness": dc.card.toughness, "loyalty": dc.card.loyalty,
                    "image_uris": {"normal": dc.card.image_url}, "prices": {"eur": str(dc.card.price_eur)},
                    "colors": dc.card.colors, "color_identity": dc.card.color_identity, "keywords": dc.card.keywords
                }
            })
    return {"id": deck.id, "name": deck.name, "description": deck.description, "cards": cards}

@app.post("/decks/{deck_id}/add")
def add_card_to_deck(deck_id: int, card_in: DeckCardAdd, db: Session = Depends(get_db)):
    card = db.query(models.CollectionCard).filter(models.CollectionCard.oracle_id == card_in.oracle_id).first()
    if not card: raise HTTPException(status_code=404)
    dc = db.query(models.DeckCard).filter(models.DeckCard.deck_id == deck_id, models.DeckCard.oracle_id == card_in.oracle_id, models.DeckCard.category == card_in.category).first()
    if dc: dc.quantity += 1
    else: db.add(models.DeckCard(deck_id=deck_id, oracle_id=card_in.oracle_id, quantity=1, category=card_in.category))
    db.commit()
    return {"status": "success"}

@app.post("/decks/{deck_id}/remove")
def remove_card_from_deck(deck_id: int, card_in: DeckCardRemove, db: Session = Depends(get_db)):
    dc = db.query(models.DeckCard).filter(models.DeckCard.deck_id == deck_id, models.DeckCard.oracle_id == card_in.oracle_id, models.DeckCard.category == card_in.category).first()
    if dc:
        if dc.quantity > 1: dc.quantity -= 1
        else: db.delete(dc)
        db.commit(); return {"status": "success"}
    raise HTTPException(status_code=404)

@app.get("/stats/value")
def get_collection_value(db: Session = Depends(get_db)):
    cards = db.query(models.CollectionCard).all()
    total_value = sum((card.price_eur or 0) * card.quantity for card in cards if (card.price_eur or 0) > 1.0)
    last = db.query(models.ValueHistory).order_by(models.ValueHistory.timestamp.desc()).first()
    if not last or (datetime.datetime.utcnow() - last.timestamp).total_seconds() > 3600:
        db.add(models.ValueHistory(total_value=total_value)); db.commit()
    history = db.query(models.ValueHistory).order_by(models.ValueHistory.timestamp).all()
    return {"total_value": total_value, "history": [{"timestamp": h.timestamp, "value": h.total_value} for h in history]}
