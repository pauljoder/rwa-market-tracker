# RWA Tokenized Treasuries - Market Analysis

A Python data analysis project tracking the growth of tokenized real-world assets (RWA) - specifically money market funds and T-bill products - deployed on public blockchains.

Built as part of my Master's thesis research on *Tokenization of Artworks as Real World Assets and their Impact on the Cultural Sector* (Paris 1 Panthéon-Sorbonne, 2025–2026).

---

## Overview

This project pulls on-chain data via the Dune Analytics API to track the expansion of tokenized treasury markets since mid-2023. It covers the main protocols active on Ethereum and other chains, and produces an interactive dashboard to visualize market structure and adoption dynamics.

Metrics tracked:
- Total AUM across tokenized treasury protocols over time
- Protocol-level breakdown by assets under management
- Unique holder growth per protocol
- On-chain distribution by blockchain

---

## Protocols covered

| Protocol | Underlying asset | Chain | Approx. AUM (Q1 2026) |
|---|---|---|---|
| Ondo Finance (USDY / OUSG) | US T-Bills | Ethereum | ~$2.1B |
| Franklin Templeton (BENJI) | Money Market Fund | Stellar / Polygon | ~$1.4B |
| Spiko | FR & US T-Bills | Ethereum | ~$1.0B |
| Superstate | US T-Bills | Ethereum | ~$650M |
| Backed Finance | T-Bills | Ethereum | ~$400M |
| Centrifuge | Private Credit | Ethereum / CFG | ~$280M |

---

## Getting started

```bash
# Clone the repository
git clone https://github.com/pauljoder/rwa-market-tracker.git
cd rwa-market-tracker

# Install dependencies
pip install -r requirements.txt

# Run the analysis
# No API key required — the script loads realistic mock data automatically
python rwa_analysis.py

# Open rwa_dashboard.html in any browser
```

---

## Project structure

```
rwa-market-tracker/
├── rwa_analysis.py       # Main analysis script and Dune API integration
├── rwa_dashboard.html    # Output: interactive Plotly dashboard
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Dashboard

The output dashboard includes four panels:

1. Total AUM over time — area chart showing the market trajectory since mid-2023
2. AUM by protocol — horizontal bar chart, latest snapshot
3. Holder growth — multi-line chart tracking unique wallet adoption across protocols
4. AUM by blockchain — donut chart showing chain distribution

---

## Dune API key (optional)

The script runs on built-in mock data by default. To connect to live on-chain data:

1. Create a free account at [dune.com](https://dune.com)
2. Go to Settings → API Keys → Create new key
3. Set the environment variable before running:

```bash
export DUNE_API_KEY="your_key_here"
```

The free tier allows approximately 1,000 API calls per month.

---

## Context

The rapid growth of tokenized treasuries represents one of the clearest proof-of-concept moments for RWA tokenization at scale. Unlike earlier blockchain-based asset experiments, these products offer genuine on-chain settlement, daily liquidity without traditional fund redemption friction, and composability with DeFi protocols, for instance, using tokenized T-bills as collateral on lending markets.

Analyzing this market's structure is directly relevant to assessing whether comparable infrastructure can eventually be applied to less liquid asset classes such as artworks or cultural heritage objects.

---

## Data sources

- [Dune Analytics](https://dune.com) — on-chain query engine
- [RWA.xyz](https://rwa.xyz) — RWA market dashboard
- [DeFiLlama](https://defillama.com/protocols/RWA) — protocol TVL tracking

---

*M1 Data Science (History & Culture) — Universite Paris 1 Pantheon-Sorbonne*
