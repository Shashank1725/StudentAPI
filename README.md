# Student Task Manager API

A production-ready RESTful API for managing student tasks built with FastAPI, SQLite, JWT authentication, and Docker.

## Features

- ✅ Complete CRUD operations for tasks
- ✅ JWT-based authentication & authorization
- ✅ User registration and management
- ✅ Task filtering, pagination, and sorting
- ✅ Input validation with Pydantic
- ✅ Structured error handling
- ✅ Automatic API documentation (Swagger UI & ReDoc)
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Containerized with Docker
- ✅ Comprehensive test suite with 80%+ coverage
- ✅ Health check endpoint

## Quick Start

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build and run with Docker
docker build -t task-manager-api .
docker run -p 8000:8000 task-manager-api