# TradeFlow Engine - Backend Technical Documentation

## Overview

TradeFlow Engine is a high-performance, asynchronous order management and matching system built with FastAPI. It handles order creation, processing, and matching through an event-driven architecture powered by Kafka, with caching via Redis and persistent storage in MySQL.

## Architecture

### Technology Stack

- **Framework**: FastAPI 0.115.0 (Python web framework)
- **Server**: Uvicorn 0.30.6 (ASGI server)
- **Database**: MySQL 8.0 with SQLAlchemy 2.0.23 ORM
- **Message Queue**: Apache Kafka (order event streaming)
- **Cache**: Redis 7 (query result caching)
- **Async Database Driver**: aiomysql 0.2.0
- **Kafka Client**: aiokafka 0.10.0
- **Data Validation**: Pydantic 2.5.0
- **Database Migrations**: Alembic 1.13.2

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Server                        │
│                      (Port 8000)                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints (/orders)                             │  │
│  │  - POST /orders (Create)                             │  │
│  │  - GET /orders (List all)                            │  │
│  │  - GET /orders/{id} (Get one)                        │  │
│  │  - GET /orders/user/{user_id} (Cached queries)       │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
           │                        │                    │
           ▼                        ▼                    ▼
    ┌─────────────┐        ┌──────────────┐      ┌─────────────┐
    │  MySQL DB   │        │  Redis Cache │      │   Kafka     │
    │  (Orders)   │        │  (Queries)   │      │  (Events)   │
    └─────────────┘        └──────────────┘      └─────────────┘
                                                           │
                                                           ▼
                                          ┌───────────────────────────┐
                                          │  Matching Engine Service   │
                                          │  (Async Consumer)          │
                                          │  - Process ORDER_PLACED    │
                                          │  - Update order status     │
                                          └───────────────────────────┘
```

## Project Structure

```
app/
├── main.py                     # FastAPI application entry point
├── matching_engine.py          # Kafka consumer for order matching
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
│
├── db/                         # Database & External Service Connections
│   ├── mysql.py               # MySQL connection & session management
│   ├── redis.py               # Redis connection & client
│   └── kafka.py               # Kafka producer & consumer setup
│
├── models/                     # SQLAlchemy ORM Models
│   └── order.py               # Order model with OrderStatus enum
│
├── schemas/                    # Pydantic validation schemas
│   └── order.py               # OrderCreate, OrderOut schemas
│
├── services/                   # Business logic layer
│   └── order_service.py        # Order creation, retrieval, caching logic
│
├── repositories/               # Data access layer
│   └── order_repo.py          # Order CRUD operations
│
└── routes/                     # API endpoint handlers
    └── orders.py              # Order endpoints
```

## Core Components

### 1. **API Layer** (`routes/orders.py`)
Exposes RESTful endpoints for order management:

- `POST /orders` - Create a new order
- `GET /orders` - Retrieve all orders
- `GET /orders/{order_id}` - Get specific order
- `GET /orders/user/{user_id}` - Get user's orders (cached)
- `GET /health` - Health check endpoint

### 2. **Service Layer** (`services/order_service.py`)
Implements business logic with three-step workflow:

1. **Database Persistence**: Save order to MySQL
2. **Event Publishing**: Publish `ORDER_PLACED` event to Kafka
3. **Cache Invalidation**: Clear Redis cache for the user's orders

Also handles intelligent caching:
- Check Redis first for user order queries (60-second TTL)
- Fall back to database if cache miss
- Automatic cache invalidation on order creation

### 3. **Data Access Layer** (`repositories/order_repo.py`)
Direct database operations using SQLAlchemy:
- Create orders
- Retrieve by ID, user_id
- Fetch all orders

### 4. **Matching Engine** (`matching_engine.py`)
Asynchronous Kafka consumer that:
- Listens to `order.events` topic
- Processes `ORDER_PLACED` events
- Simulates order matching (3-second delay)
- Updates order status to `FILLED` in database

### 5. **Database Layer** (`db/`)

**MySQL** (`db/mysql.py`):
- Async connection management with `create_async_engine`
- Auto-creates tables on startup via SQLAlchemy
- Session management for request handling

**Redis** (`db/redis.py`):
- Redis client for caching user order queries
- Key pattern: `user:{user_id}:orders`
- 60-second expiration time

**Kafka** (`db/kafka.py`):
- Producer for publishing order events
- Consumer for the matching engine
- Topic: `order.events`
- Event format: JSON-encoded order data

### 6. **Models** (`models/order.py`)

```python
Order Table:
├── id (PRIMARY KEY, auto-increment)
├── user_id (indexed)
├── item (string, 255 chars)
├── amount (decimal, 10,2)
└── status (OPEN, FILLED, CANCELLED)
```

## Running the Application

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (recommended)
- MySQL 8.0 (if running locally)
- Redis 7+ (if running locally)
- Apache Kafka (if running locally)

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up --build
```

This starts:
- FastAPI server on `http://localhost:8000`
- MySQL on `localhost:3306`
- Redis on `localhost:6379`
- Kafka will need separate setup (see below for local development)

### Option 2: Local Development

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export DATABASE_URL="mysql+aiomysql://user:password@localhost:3306/orders"
   export REDIS_URL="redis://localhost:6379/0"
   export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
   ```

3. **Run the server:**
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Run the matching engine (in separate terminal):**
   ```bash
   cd app
   python matching_engine.py
   ```

## API Endpoints

### Create Order
```bash
POST /orders
Content-Type: application/json

{
  "user_id": 1,
  "item": "AAPL",
  "amount": 150.50
}

Response (201):
{
  "id": 1,
  "user_id": 1,
  "item": "AAPL",
  "amount": "150.50",
  "status": "OPEN"
}
```

### Get All Orders
```bash
GET /orders

Response (200):
[
  {
    "id": 1,
    "user_id": 1,
    "item": "AAPL",
    "amount": "150.50",
    "status": "FILLED"
  }
]
```

### Get User Orders (Cached)
```bash
GET /orders/user/1

Response (200):
[
  {
    "id": 1,
    "user_id": 1,
    "item": "AAPL",
    "amount": "150.50",
    "status": "OPEN"
  }
]
```

### Get Specific Order
```bash
GET /orders/1

Response (200):
{
  "id": 1,
  "user_id": 1,
  "item": "AAPL",
  "amount": "150.50",
  "status": "FILLED"
}
```

### Health Check
```bash
GET /health

Response (200):
{
  "status": "healthy"
}
```

## Data Flow Example

1. **User creates an order:**
   ```
   Client → POST /orders → OrderService.create_order()
   ```

2. **Service processes request:**
   - Save to MySQL
   - Publish event to Kafka topic `order.events`
   - Invalidate Redis cache for user

3. **Matching engine processes:**
   - Consumes `ORDER_PLACED` event from Kafka
   - Simulates 3-second matching delay
   - Updates order status to `FILLED` in MySQL

4. **Next query for user orders:**
   - Checks Redis cache (miss, was invalidated)
   - Queries MySQL
   - Caches result for 60 seconds
   - Returns to client

## Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `mysql+aiomysql://user:password@localhost:3306/orders` | MySQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker address |

### Database Migrations (Alembic)
```bash
# Initialize migration (already done)
alembic init alembic

# Generate migration after model changes
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# View migration history
alembic history
```

## Development

### Adding New Models
1. Create model in `app/models/`
2. Generate Alembic migration: `alembic revision --autogenerate -m "description"`
3. Create Pydantic schema in `app/schemas/`
4. Create repository in `app/repositories/`
5. Create service in `app/services/`
6. Create routes in `app/routes/`

### Debugging
- Check container logs: `docker-compose logs -f app`
- MySQL logs: `docker-compose logs -f db`
- Redis logs: `docker-compose logs -f redis`
- Use `print()` statements (async-safe)

## Performance Considerations

1. **Caching Strategy**: User order queries cached for 60 seconds to reduce DB load
2. **Async/Await**: All I/O operations are non-blocking
3. **Connection Pooling**: SQLAlchemy manages connection pool automatically
4. **Event-Driven**: Kafka decouples order matching from API responses
5. **Indexing**: `user_id` indexed in orders table for fast queries

## Security Notes

- `.env` file should contain sensitive credentials (not in version control)
- MySQL credentials in docker-compose.yml are for development only
- In production, use secrets management (AWS Secrets, Azure Key Vault, etc.)
- Validate all Pydantic inputs on API endpoints
- Use HTTPS in production

## Troubleshooting

### "Connection refused" errors
- Verify Docker containers are running: `docker-compose ps`
- Check port availability: MySQL (3306), Redis (6379), FastAPI (8000)

### Kafka not processing events
- Ensure Kafka is running and reachable
- Check topic exists: `order.events`
- Verify consumer group configuration
- Check logs in matching engine

### Redis cache not working
- Verify Redis is running and accessible
- Check `REDIS_URL` environment variable
- Monitor cache hits/misses with `redis-cli`

### Database query timeouts
- Increase connection pool size in MySQL config
- Check for long-running queries
- Monitor database CPU/memory usage
