# AdWise AI Digital Marketing Campaign Builder - Project Structure

## Modular Architecture Overview

```
adwise-ai-campaign-builder/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   │
│   ├── core/                            # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py                    # Environment configuration
│   │   ├── security.py                  # Authentication & authorization
│   │   ├── database/                    # Database configuration
│   │   │   ├── __init__.py
│   │   │   ├── connection.py            # Database connections
│   │   │   ├── session.py               # Session management
│   │   │   └── migrations/              # Alembic migrations
│   │   ├── cache/                       # Redis caching layer
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # Redis client
│   │   │   └── strategies.py            # Caching strategies
│   │   ├── logging/                     # Logging configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   └── exceptions/                  # Custom exceptions
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── handlers.py
│   │
│   ├── models/                          # Database models
│   │   ├── __init__.py
│   │   ├── base.py                      # Base model classes
│   │   ├── user.py                      # User management models
│   │   ├── campaign.py                  # Campaign models
│   │   ├── content.py                   # Content models
│   │   ├── analytics.py                 # Analytics models
│   │   └── collaboration.py             # Collaboration models
│   │
│   ├── schemas/                         # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py                      # Base schema classes
│   │   ├── user.py                      # User schemas
│   │   ├── campaign.py                  # Campaign schemas
│   │   ├── content.py                   # Content schemas
│   │   ├── analytics.py                 # Analytics schemas
│   │   └── responses.py                 # API response schemas
│   │
│   ├── api/                             # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                      # Dependencies
│   │   ├── v1/                          # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Authentication endpoints
│   │   │   ├── users.py                 # User management
│   │   │   ├── campaigns.py             # Campaign management
│   │   │   ├── content.py               # Content generation
│   │   │   ├── analytics.py             # Analytics endpoints
│   │   │   ├── collaboration.py         # Real-time collaboration
│   │   │   └── ai.py                    # AI-powered features
│   │   └── middleware/                  # Custom middleware
│   │       ├── __init__.py
│   │       ├── cors.py
│   │       ├── rate_limiting.py
│   │       └── logging.py
│   │
│   ├── services/                        # Business logic layer
│   │   ├── __init__.py
│   │   ├── base.py                      # Base service class
│   │   ├── user_service.py              # User business logic
│   │   ├── campaign_service.py          # Campaign business logic
│   │   ├── content_service.py           # Content generation logic
│   │   ├── analytics_service.py         # Analytics processing
│   │   ├── collaboration_service.py     # Real-time collaboration
│   │   └── ai/                          # AI services
│   │       ├── __init__.py
│   │       ├── content_generator.py     # AI content generation
│   │       ├── campaign_optimizer.py    # Campaign optimization
│   │       ├── analytics_ai.py          # AI-powered analytics
│   │       └── embeddings.py            # Vector embeddings
│   │
│   ├── repositories/                    # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                      # Base repository class
│   │   ├── user_repository.py           # User data access
│   │   ├── campaign_repository.py       # Campaign data access
│   │   ├── content_repository.py        # Content data access
│   │   ├── analytics_repository.py      # Analytics data access
│   │   └── collaboration_repository.py  # Collaboration data access
│   │
│   ├── integrations/                    # External integrations
│   │   ├── __init__.py
│   │   ├── euri/                        # EURI API integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # EURI client
│   │   │   ├── models.py                # EURI data models
│   │   │   └── services.py              # EURI services
│   │   ├── langchain/                   # LangChain integration
│   │   │   ├── __init__.py
│   │   │   ├── chains.py                # LangChain chains
│   │   │   ├── agents.py                # LangChain agents
│   │   │   └── tools.py                 # Custom tools
│   │   └── social_media/                # Social media platforms
│   │       ├── __init__.py
│   │       ├── facebook.py
│   │       ├── instagram.py
│   │       ├── twitter.py
│   │       └── linkedin.py
│   │
│   ├── utils/                           # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py                # Data validation utilities
│   │   ├── formatters.py                # Data formatting utilities
│   │   ├── file_handlers.py             # File processing utilities
│   │   ├── email.py                     # Email utilities
│   │   └── security.py                  # Security utilities
│   │
│   ├── tasks/                           # Background tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py                # Celery configuration
│   │   ├── campaign_tasks.py            # Campaign-related tasks
│   │   ├── analytics_tasks.py           # Analytics processing tasks
│   │   ├── ai_tasks.py                  # AI processing tasks
│   │   └── notification_tasks.py        # Notification tasks
│   │
│   └── websockets/                      # WebSocket handlers
│       ├── __init__.py
│       ├── manager.py                   # WebSocket connection manager
│       ├── collaboration.py             # Real-time collaboration
│       └── notifications.py             # Real-time notifications
│
├── frontend/                            # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/                  # Reusable components
│   │   ├── pages/                       # Page components
│   │   ├── hooks/                       # Custom React hooks
│   │   ├── services/                    # API services
│   │   ├── store/                       # State management
│   │   ├── utils/                       # Utility functions
│   │   └── types/                       # TypeScript types
│   ├── package.json
│   └── tsconfig.json
│
├── tests/                               # Test suite
│   ├── __init__.py
│   ├── conftest.py                      # Test configuration
│   ├── unit/                            # Unit tests
│   ├── integration/                     # Integration tests
│   ├── e2e/                             # End-to-end tests
│   └── fixtures/                        # Test fixtures
│
├── docs/                                # Documentation
│   ├── api/                             # API documentation
│   ├── deployment/                      # Deployment guides
│   └── development/                     # Development guides
│
├── scripts/                             # Utility scripts
│   ├── setup.py                         # Environment setup
│   ├── migrate.py                       # Database migrations
│   └── seed.py                          # Database seeding
│
├── docker/                              # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│
├── .env.example                         # Environment variables template
├── .gitignore
├── requirements.txt                     # Python dependencies
├── pyproject.toml                       # Python project configuration
├── README.md
└── LICENSE
```

## Key Architectural Principles

### 1. Separation of Concerns
- **Models**: Database schema and relationships
- **Schemas**: API input/output validation
- **Services**: Business logic and orchestration
- **Repositories**: Data access abstraction
- **API**: HTTP endpoint definitions

### 2. Dependency Injection
- Clear dependency flow from API → Services → Repositories
- Easy testing and mocking
- Configurable components

### 3. Modular Design
- Each module has a single responsibility
- Clear interfaces between modules
- Easy to extend and maintain

### 4. Database Strategy
- **PostgreSQL**: Primary database with JSONB for flexible data
- **Redis**: Caching and real-time features
- **Vector Extensions**: AI embeddings and similarity search

### 5. AI Integration
- **EURI API**: External AI service integration
- **LangChain**: AI workflow orchestration
- **LangGraph**: Complex AI agent workflows
- **LangServe**: AI service deployment

### 6. Real-time Features
- **WebSockets**: Real-time collaboration
- **Redis Pub/Sub**: Event broadcasting
- **Background Tasks**: Async processing

This structure ensures:
- **Scalability**: Easy to scale individual components
- **Maintainability**: Clear code organization
- **Testability**: Isolated components for testing
- **Flexibility**: Easy to modify or extend features
- **Performance**: Optimized data access patterns
