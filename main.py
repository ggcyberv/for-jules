import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add the current directory to sys.path so 'backend' can be found
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    print("========================================")
    print("   MTG Collection App Backend")
    print("========================================")
    print("Starting server at http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server.")
    print("----------------------------------------")

    try:
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"Error starting server: {e}")
