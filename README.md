# Stock Intelligence Copilot

## Overview
An AI-assisted stock market analysis system for retail investors. Provides probabilistic insights, never guarantees. Read-only by design.

## Core Principles
- **Assistive, not automated**: Suggestions only, no trade execution
- **Probabilistic**: Confidence scores, never certainty
- **Explainable**: Clear reasoning for every insight
- **Risk-aware**: Built-in safety constraints

## Architecture
```
backend/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Core business logic
│   │   ├── market_data/  # Data ingestion
│   │   ├── indicators/   # Technical indicators
│   │   ├── signals/      # Signal generation
│   │   ├── risk/         # Risk assessment
│   │   ├── explanation/  # Reasoning layer
│   │   └── orchestrator/ # Pipeline coordinator
│   ├── models/           # Pydantic data models
│   └── config/           # Configuration
├── tests/                # Unit tests
└── main.py               # Application entry point
```

## MVP Capabilities
- Analyze stock data (price, volume, indicators)
- Generate Bullish/Bearish/Neutral signals with confidence
- Explain reasoning and assumptions
- Enforce risk constraints
- Long-term investing focus (default)

## Not Included in MVP
- Trade execution
- Exact price predictions
- Real broker API integration
- Frontend UI
- User authentication

## Getting Started
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## API Endpoints
- `GET /health` - Health check
- `POST /api/v1/analyze` - Analyze a stock
- `GET /api/v1/supported-tickers` - Get supported tickers

## Safety Notes
- All outputs are suggestions, not financial advice
- No guarantees of returns or accuracy
- "No action recommended" is a valid outcome
- Users must do their own research
