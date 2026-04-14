from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, JSON
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

# Many-to-many relationship for Card Tags
card_tag_association = Table(
    'card_tag', Base.metadata,
    Column('oracle_id', String, ForeignKey('collection_cards.oracle_id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class CollectionCard(Base):
    __tablename__ = 'collection_cards'

    oracle_id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    quantity = Column(Integer, default=0)

    # Cached Scryfall data
    type_line = Column(String, index=True)
    mana_cost = Column(String)
    cmc = Column(Float)
    oracle_text = Column(String)
    colors = Column(JSON) # List of colors on the card
    color_identity = Column(JSON) # List of colors in identity (includes symbols in text)
    image_url = Column(String)
    price_eur = Column(Float, index=True)
    legalities = Column(JSON)
    keywords = Column(JSON)

    tags = relationship("Tag", secondary=card_tag_association, back_populates="cards")
    deck_cards = relationship("DeckCard", back_populates="card")

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    cards = relationship("CollectionCard", secondary=card_tag_association, back_populates="tags")

class Deck(Base):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)

    cards = relationship("DeckCard", back_populates="deck")

class DeckCard(Base):
    __tablename__ = 'deck_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(Integer, ForeignKey('decks.id'))
    oracle_id = Column(String, ForeignKey('collection_cards.oracle_id'))
    quantity = Column(Integer, default=1)
    category = Column(String) # e.g., 'Main', 'Considering', 'History'

    deck = relationship("Deck", back_populates="cards")
    card = relationship("CollectionCard", back_populates="deck_cards")

class ValueHistory(Base):
    __tablename__ = 'value_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    total_value = Column(Float, nullable=False)

class APICache(Base):
    __tablename__ = 'api_cache'

    query_key = Column(String, primary_key=True) # e.g., 'autocomplete:Griz' or 'search:island'
    response_json = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
