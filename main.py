import uvicorn
import os

if __name__ == "__main__":
    # Ensure the database is initialized (done in backend/main.py)
    print("Starting MTG Collection App Backend...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
