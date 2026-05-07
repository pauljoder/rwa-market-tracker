"""
RWA Tokenized Treasuries — Market Analysis
===========================================
Pulls on-chain data via Dune Analytics API to track the growth
of tokenized real-world assets (money market funds, T-bills) on Ethereum.

Protocols covered: Spiko, Ondo Finance (USDY/OUSG), Franklin Templeton (BENJI),
                   Backed Finance, Centrifuge, Superstate

Author: Paul Joder
"""

import os
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

DUNE_API_KEY = os.getenv("DUNE_API_KEY", "YOUR_API_KEY_HERE")
HEADERS = {"X-Dune-API-Key": DUNE_API_KEY}
BASE_URL = "https://api.dune.com/api/v1"

# Dune query IDs (public queries — swap with your own forks for customisation)
QUERIES = {
    "rwa_aum_over_time":  3705913,   # Total tokenized treasury AUM over time
    "rwa_by_protocol":    3705914,   # AUM breakdown by protocol
    "rwa_holder_count":   3705915,   # Unique holders per protocol
    "rwa_chain_breakdown": 3705916,  # AUM by blockchain (Ethereum, Polygon, Stellar…)
}


# ── Dune API helpers ───────────────────────────────────────────────────────────

def fetch_query_results(query_id: int) -> pd.DataFrame:
    """Fetch latest results for a Dune query and return as DataFrame."""
    url = f"{BASE_URL}/query/{query_id}/results"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    rows = data["result"]["rows"]
    return pd.DataFrame(rows)


def fetch_all_queries() -> dict[str, pd.DataFrame]:
    """Fetch all configured queries. Falls back to mock data if API key missing."""
    if DUNE_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  No API key found — loading mock data for demonstration.")
        return load_mock_data()

    results = {}
    for name, qid in QUERIES.items():
        print(f"  Fetching '{name}' (query {qid})…")
        results[name] = fetch_query_results(qid)
    return results


# ── Mock data (runs without API key) ─────────────────────────────────────────

def load_mock_data() -> dict[str, pd.DataFrame]:
    """
    Realistic mock data based on public RWA.xyz / DeFiLlama figures (Q1 2026).
    Useful for local development and demonstration purposes.
    """
    import numpy as np

    # AUM over time — weekly snapshots (USD millions)
    dates = pd.date_range("2023-06-01", "2026-03-01", freq="W")
    aum_values = np.linspace(50, 6000, len(dates)) + np.random.normal(0, 80, len(dates))
    aum_values = np.clip(aum_values, 50, None)
    aum_growth = pd.DataFrame({
        "date": dates,
        "total_aum_usd": aum_values
    })

    # AUM by protocol (latest snapshot)
    protocol_aum = pd.DataFrame({
        "protocol":   ["Ondo Finance", "Franklin Templeton", "Spiko",
                       "Superstate", "Backed Finance", "Centrifuge"],
        "aum_usd_m":  [2100, 1400, 1000, 650, 400, 280],
        "chain":      ["Ethereum", "Stellar/Polygon", "Ethereum",
                       "Ethereum", "Ethereum", "Ethereum/Centrifuge"],
        "asset_type": ["T-Bills", "Money Market", "T-Bills (FR/US)",
                       "T-Bills", "T-Bills", "Private Credit"],
        "yield_pct":  [5.1, 4.9, 3.8, 5.0, 4.7, 6.2],
    })

    # Holder count over time
    holder_dates = pd.date_range("2024-01-01", "2026-03-01", freq="ME")
    holders = pd.DataFrame({
        "date": holder_dates,
        "Ondo Finance":        [120, 180, 260, 380, 500, 680, 850, 1100,
                                1400, 1800, 2300, 2900, 3500, 4200, 5000,
                                5900, 6800, 7800, 8900, 10100, 11500, 13000, 14700, 16500, 18200, 20000],
        "Spiko":               [10,  20,  40,  80,  140, 220, 350, 550,
                                800, 1100, 1500, 2000, 2700, 3500, 4400,
                                5500, 6700, 8000, 9500, 11100, 12800, 14600, 16500, 18500, 20600, 22800],
        "Franklin Templeton":  [50,  90,  150, 220, 300, 400, 520, 660,
                                820, 1000, 1200, 1430, 1700, 2000, 2350,
                                2750, 3200, 3700, 4300, 4950, 5650, 6400, 7200, 8100, 9100, 10200],
    })

    # Chain breakdown
    chain_data = pd.DataFrame({
        "chain":      ["Ethereum", "Stellar", "Polygon", "Solana", "Other"],
        "aum_usd_m":  [4100, 1400, 600, 250, 480],
    })

    return {
        "rwa_aum_over_time":   aum_growth,
        "rwa_by_protocol":     protocol_aum,
        "rwa_holder_count":    holders,
        "rwa_chain_breakdown": chain_data,
    }


# ── Analysis functions ────────────────────────────────────────────────────────

def compute_growth_metrics(df: pd.DataFrame) -> dict:
    """Compute key growth KPIs from the AUM time series."""
    df = df.sort_values("date")
    latest = df["total_aum_usd"].iloc[-1]
    one_year_ago = df[df["date"] <= df["date"].iloc[-1] - pd.DateOffset(years=1)]
    yoy = ((latest / one_year_ago["total_aum_usd"].iloc[-1]) - 1) * 100 if len(one_year_ago) else None

    first = df["total_aum_usd"].iloc[0]
    n_months = (df["date"].iloc[-1] - df["date"].iloc[0]).days / 30
    cagr = ((latest / first) ** (12 / n_months) - 1) * 100

    return {
        "latest_aum_usd_m": round(latest, 1),
        "yoy_growth_pct":   round(yoy, 1) if yoy else "N/A",
        "monthly_cagr_pct": round(cagr, 1),
        "data_start":       df["date"].iloc[0].strftime("%Y-%m"),
    }


# ── Visualisation ─────────────────────────────────────────────────────────────

def build_dashboard(data: dict) -> go.Figure:
    """Build a multi-panel Plotly dashboard."""

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Total RWA Tokenized Treasuries AUM (USD M)",
            "AUM by Protocol — Latest Snapshot",
            "Unique Holder Growth by Protocol",
            "AUM by Blockchain",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "pie"}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    COLORS = px.colors.qualitative.Set2

    # ── Panel 1 : total AUM over time ─────────────────────────────────────────
    df_aum = data["rwa_aum_over_time"].copy()
    df_aum["date"] = pd.to_datetime(df_aum["date"])
    fig.add_trace(
        go.Scatter(
            x=df_aum["date"], y=df_aum["total_aum_usd"],
            mode="lines", fill="tozeroy",
            line=dict(color="#3B82F6", width=2),
            fillcolor="rgba(59,130,246,0.15)",
            name="Total AUM",
        ),
        row=1, col=1,
    )

    # ── Panel 2 : protocol breakdown ─────────────────────────────────────────
    df_proto = data["rwa_by_protocol"].sort_values("aum_usd_m", ascending=True)
    fig.add_trace(
        go.Bar(
            x=df_proto["aum_usd_m"], y=df_proto["protocol"],
            orientation="h",
            marker_color=COLORS[:len(df_proto)],
            text=df_proto["aum_usd_m"].apply(lambda v: f"${v}M"),
            textposition="outside",
            name="AUM by Protocol",
        ),
        row=1, col=2,
    )

    # ── Panel 3 : holder growth ───────────────────────────────────────────────
    df_holders = data["rwa_holder_count"].copy()
    df_holders["date"] = pd.to_datetime(df_holders["date"])
    for i, col in enumerate([c for c in df_holders.columns if c != "date"]):
        fig.add_trace(
            go.Scatter(
                x=df_holders["date"], y=df_holders[col],
                mode="lines", name=col,
                line=dict(color=COLORS[i], width=2),
            ),
            row=2, col=1,
        )

    # ── Panel 4 : chain breakdown ─────────────────────────────────────────────
    df_chain = data["rwa_chain_breakdown"]
    fig.add_trace(
        go.Pie(
            labels=df_chain["chain"], values=df_chain["aum_usd_m"],
            marker_colors=COLORS,
            textinfo="label+percent",
            hole=0.35,
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title=dict(
            text="RWA Tokenized Treasuries — On-chain Market Dashboard",
            font=dict(size=18),
        ),
        height=750,
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=60, r=40),
    )
    return fig


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("=== RWA Tokenized Treasuries — Analysis ===\n")
    print("Fetching data from Dune Analytics…")
    data = fetch_all_queries()

    metrics = compute_growth_metrics(data["rwa_aum_over_time"])
    print("\n📊 Key Metrics:")
    print(f"  Latest AUM   : ${metrics['latest_aum_usd_m']}M")
    print(f"  YoY Growth   : {metrics['yoy_growth_pct']}%")
    print(f"  Monthly CAGR : {metrics['monthly_cagr_pct']}%")
    print(f"  Data since   : {metrics['data_start']}")

    print("\n🏆 Top Protocols by AUM:")
    df_proto = data["rwa_by_protocol"].sort_values("aum_usd_m", ascending=False)
    print(df_proto[["protocol", "aum_usd_m", "yield_pct", "asset_type"]].to_string(index=False))

    print("\nBuilding dashboard…")
    fig = build_dashboard(data)
    fig.write_html("rwa_dashboard.html")
    print("✅ Dashboard saved → rwa_dashboard.html")


if __name__ == "__main__":
    main()
