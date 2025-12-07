# TradeFlow-Engine

TradeFlow-Engine is a high-performance crypto order tracking microservice built with FastAPI, Redis, MySQL, and SQLModel. It demonstrates a cache-aside pattern using Redis for low-latency reads of recent open orders, backed by persistent storage in MySQL. This project is designed to be a foundation for trading and crypto exchange products with scalable API and event-driven architecture.

---

## Features

- FastAPI REST API for user and order management
- Async MySQL integration using SQLModel and `aiomysql`
- Redis cache-aside pattern for low-latency open order queries
- Alembic migrations for database schema versioning
- Docker Compose setup for MySQL and Redis for easy local development

---

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [SQLModel](https://sqlmodel.tiangolo.com/) — Async ORM toolkit
- [MySQL](https://www.mysql.com/) — Relational database (via Docker)
- [Redis](https://redis.io/) — In-memory cache (via Docker)
- [Alembic](https://alembic.sqlalchemy.org/) — DB migrations
- `pymysql` and `aiomysql` — MySQL drivers for sync and async access

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Python 3.10+

### Installation and Run

1. Clone the repo:

```bash
git clone https://github.com/yourusername/TradeFlow-Engine.git
cd TradeFlow-Engine
```

2. Start MySQL and Redis via Docker Compose:

```bash
docker-compose up -d
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Run Alembic migrations to create DB schema:

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

5. Start the API server:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## API Endpoints

| Method | Endpoint                       | Description                     |
| ------ | ------------------------------ | ------------------------------- |
| POST   | `/users/`                      | Create a new user               |
| POST   | `/orders/`                     | Place a new order               |
| GET    | `/users/{user_id}/open-orders` | Get user's open orders (cached) |

---

## Cache-Aside Pattern

- Reads first check Redis cache.
- Cache misses fetch from MySQL and populate Redis.
- Writes invalidate relevant Redis keys to keep cache consistent.

This pattern reduces MySQL read load and improves API responsiveness during high traffic.
