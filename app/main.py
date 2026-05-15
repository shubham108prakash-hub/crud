from fastapi import FastAPI
from app.database import engine, Base
from app.routes import users, notes

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes API",
    description="A multi-user notes service with sharing, search, and label support.",
    version="1.0.0",
)

# Include route modules
app.include_router(users.router, tags=["Auth"])
app.include_router(notes.router, tags=["Notes"])


@app.get("/about")
def about():
    return {
        "name": "Shubham Prakash",
        "email": "shubham@example.com",
        "my features": {
            "Full-text search": "GET /search?q=keyword – Lets users quickly find notes by title or content using ILIKE pattern matching. Chose it because search is the most natural way to navigate a growing collection of notes.",
            "Pagination": "GET /notes?page=1&per_page=20 – Optional pagination on the notes listing endpoint to keep responses fast when a user has hundreds of notes.",
            "Note labels / tags": "POST /notes/{id}/labels, GET /notes?label=work – Users can attach labels to notes and filter by label, making organisation effortless. Chose it because flat note lists don't scale; labels add structure without complexity.",
        },
    }
