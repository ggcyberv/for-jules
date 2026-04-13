# MTG Collection & Deck Manager

A modern, PC-based application for tracking your Magic: The Gathering card collection and managing decks.

## Quick Start (Single Command)

From the root directory:

```bash
# Install all dependencies (Backend and Frontend)
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Start the application (starts both Backend and Frontend)
python main.py
```

- **Frontend:** http://localhost:5173
- **Backend (API):** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Features

- **Local Caching:** Card metadata and prices from Scryfall are cached locally in a SQLite database for lightning-fast performance.
- **Scryfall Integration:** Add cards by name or set code. Supports English and German card names.
- **Advanced Filtering:** Filter your collection by color, card type, format legality, keywords, and more.
- **Deck Management:** Organize decks with categorization by card type (Creature, Land, etc.) and status (Mainboard, Considering, History).
- **Collection Valuation:** Track the financial value of your collection with historical graphs (tracks cards > €1).
- **Two Display Modes:** Switch between a visual image grid and a functional text-based list view.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy (SQLite), Scryfall API.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
