# FastAPI Notes Service

A minimal, production-ready backend for a multi-user notes application built with FastAPI and SQLite. 

## Features

- **User Authentication:** Secure user registration and login using JWT (JSON Web Tokens) and bcrypt password hashing.
- **Notes Management:** Full CRUD (Create, Read, Update, Delete) operations for notes.
- **Note Sharing:** Seamlessly share notes with other registered users via email.
- **Full-Text Search:** Users can search across all their own and shared notes by title or content using a single search query.
- **Pagination:** Note listing endpoints support optional pagination (`page` and `per_page` query parameters) for efficient data retrieval.
- **Labels (Tags):** Users can create, attach, and remove labels from notes to categorize them. Notes can also be filtered by label.
- **Database:** Uses SQLite for lightweight, file-based data storage, managed via SQLAlchemy ORM.
- **Data Validation:** Strict input validation and serialization using Pydantic schemas.
- **Dockerized:** Fully containerized with a `Dockerfile` for straightforward deployment to platforms like Render or AWS.
- **Interactive API Documentation:** Automatic Swagger UI documentation provided out-of-the-box by FastAPI.

## Project Structure

```
├── app/
│   ├── routes/
│   │   ├── notes.py    # Endpoints for note CRUD and sharing
│   │   └── users.py    # Endpoints for registration and login
│   ├── auth.py         # JWT and password hashing utilities
│   ├── database.py     # SQLAlchemy setup and session management
│   ├── models.py       # Database models (SQLAlchemy)
│   ├── schemas.py      # Pydantic models for request/response validation
│   └── main.py         # FastAPI application entry point
├── Dockerfile          # Instructions to build the Docker image
└── requirements.txt    # Python dependencies
```

## Technologies Used

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Authentication:** `python-jose` (JWT), `passlib` (bcrypt)
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/)
- **Server:** [Uvicorn](https://www.uvicorn.org/)
