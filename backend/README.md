# Investment Agent

An AI-first investment research project built with LangGraph + Python, focused on combining quantitative signals, sentiment, fundamentals, and document intelligence into a modular decision workflow.

## Vision

This project follows an **8-pillar modular architecture**:

1. **Price Prediction (Quant Node)**  
   Forecast expected price range and volatility envelope (not exact price).
2. **Trend Follow (Regime Filter A)**  
   Track market direction with low-latency technical features.
3. **Bull/Bear Signal (Regime Filter B)**  
   Detect regime state and adjust confidence of trend signals.
4. **Risk Management (Governor / Veto Layer)**  
   Use probabilistic simulation to approve, reject, or reduce position size.
5. **Fundamental Potential (Context Node A)**  
   Rank quality and growth potential with multi-factor scoring.
6. **Sector Trends (Context Node B)**  
   Apply top-down sector headwind/tailwind adjustment.
7. **News Sentiment (Intelligence Node A)**  
   Transform financial news into actionable sentiment/risk events.
8. **RAG on 10-K / 10-Q (Intelligence Node B)**  
   Extract management guidance and structural risks from filings.

## Execution Graph

The system is designed as **parallel-then-merge** instead of a linear chain:

- **Level 1 (Data Fetch):** collect structured market data + unstructured filing/news data
- **Level 2 (Parallel Analysis):**
  - Path A: Pillars 1/2/3 (technical and regime signals)
  - Path B: Pillars 5/6/7/8 (fundamental and intelligence signals)
- **Level 3 (Synthesis):** a reasoning node combines Path A + Path B
- **Level 4 (Risk Gate):** Pillar 4 can veto or downsize the action

## Design Principles

- **Low latency where needed:** price/trend/regime use direct Python math and ML
- **LLMs where useful:** sentiment and filing analysis use LLM/RAG components
- **Modular scoring:** each pillar emits a normalized score + confidence
- **Risk-first output:** no trade idea bypasses the governor
- **Explainability:** outputs include evidence, not just signals

## Current Capabilities

- Fetch stock/index data and historical prices
- Technical analysis tools (trend follow, mean reversion, filters)
- Fundamental + news fetching in one tool path
- Stateful agent orchestration with LangGraph
- Local-first development with Ollama-compatible models

## Roadmap

### Phase 1: Signal MVP (now)

- Stabilize Pillar 2 (Trend Follow)
- Build Pillar 7 (News Sentiment) baseline
- Merge both into one simple long/neutral/avoid signal

### Phase 2: Intelligence Upgrade

- Add Pillar 8 with filing retrieval + chunking + citation
- Add cross-check logic between news events and filing risks

### Phase 3: Risk and Portfolio Controls

- Implement Pillar 4 veto with Monte Carlo tail-risk checks
- Add position sizing and max drawdown constraints

### Phase 4: Production Readiness

- Containerize services (Docker)
- Add orchestration profile (Kubernetes/OpenShift compatible)
- Add observability: latency, hit ratio, and signal quality dashboards
- Add A/B evaluation pipeline for strategy variants

## Local Training and Compute Plan

Local hardware target: **RTX 5070 Ti + AMD Ryzen 9 + 32 GB RAM**

- Run feature engineering and classical ML locally (XGBoost/LightGBM)
- Run sentiment experiments with lightweight/frozen encoders first
- Use parameter-efficient fine-tuning only when required
- Cache embeddings/features to reduce repeated compute costs
- Keep training reproducible with versioned datasets and configs

## Deployment Strategy (Cost-Aware)

- Start with local + single small cloud instance for API hosting
- Use managed Postgres only when usage grows
- Run scheduled batch jobs for heavy analysis to control costs
- Keep real-time path limited to light computations
- Stay cloud-agnostic in code (portable between Azure/AWS/GCP)

## Project Structure

```text
.
├── db/
│   ├── data/
│   │   └── HSI.csv
│   ├── schema/
│   │   └── core_table.sql
│   ├── init_db.py
│   └── load_csv.py
├── src/
│   ├── chatroom/
│   │   └── app.py
│   ├── prompts/
│   │   └── investment_agent.py
│   ├── tools/
│   │   ├── analysis.py
│   │   ├── crypto.py
│   │   └── stock.py
│   ├── schemas/
│   │   └── ticker_schema.py
│   └── agent.py
├── main.py
└── requirements.txt
```

## Setup

```bash
# Clone the repository
git clone https://github.com/ManJ0405/investment_agent.git
cd investment_agent/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the project
python main.py run
```

## Next Milestones

- [ ] Pillar 2 signal reliability backtest
- [ ] Pillar 7 sentiment baseline model
- [ ] Unified scoring schema across all pillars
- [ ] Risk governor prototype with veto output
- [ ] End-to-end paper trading simulation

## Author

ManJ0405


