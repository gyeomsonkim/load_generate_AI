# Pathfinding Server Project Structure

```
pathfinding-server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── maps.py        # Map upload/management endpoints
│   │   │   ├── pathfinding.py # Pathfinding endpoints
│   │   │   └── health.py      # Health check endpoints
│   │   └── dependencies.py    # Shared dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pathfinding/
│   │   │   ├── __init__.py
│   │   │   ├── algorithms.py  # A* and other pathfinding algorithms
│   │   │   ├── preprocessor.py # Image preprocessing
│   │   │   └── graph.py       # Graph representation of maps
│   │   └── ml/
│   │       ├── __init__.py
│   │       ├── models.py      # ML models (Phase 2)
│   │       └── detector.py    # Path/obstacle detection (Phase 2)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py        # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── enums.py          # Enum definitions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── map_service.py     # Map management logic
│   │   ├── storage_service.py # File storage logic
│   │   └── pathfinding_service.py # Pathfinding business logic
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py     # Image processing utilities
│       └── coordinates.py     # Coordinate conversion utilities
├── storage/
│   ├── uploads/               # Uploaded original images
│   └── processed/             # Preprocessed images
├── ml_models/                 # Trained ML models (Phase 2)
├── tests/
│   ├── __init__.py
│   ├── test_api/
│   ├── test_core/
│   └── test_services/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
└── setup.py
```