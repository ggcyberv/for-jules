# MTG Collection & Deck Manager

A modern, PC-based application for tracking your Magic: The Gathering card collection and managing decks.

## Features

- **Local Caching:** Card metadata and prices from Scryfall are cached locally in a SQLite database for lightning-fast performance.
- **Scryfall Integration:** Add cards by name or set code. Supports English and German card names.
- **Advanced Filtering:** Filter your collection by color, card type, format legality, keywords, and more.
- **Deck Management:** Organize decks with categorization by card type (Creature, Land, etc.) and status (Mainboard, Considering, History).
- **Collection Valuation:** Track the financial value of your collection with historical graphs (tracks cards > €1).
- **Two Display Modes:** Switch between a visual image grid and a functional text-based list view.

## Requirements

- Python 3.8+
- Node.js 18+

## Setup Instructions

### 1. Backend Setup

From the root directory:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend runs on `http://localhost:8000`.

### 2. Frontend Setup

From the `frontend` directory:

```bash
# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy (SQLite), Scryfall API.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
