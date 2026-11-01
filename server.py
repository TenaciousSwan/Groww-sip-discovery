"""
Groww SIP Discovery Engine - High-Performance FastAPI Server (server.py)
-------------------------------------------------------------------------
Lightweight backend (<40MB RAM, sub-second boot) replacing Streamlit.
Provides REST API endpoints for telemetry, behavioral insights, opportunity sizing,
benchmark logs, and real-time LLM diagnostics.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import pandas as pd
from analyzer import (
    analyze_review,
    classify_with_heuristic_engine,
    compute_opportunity_rankings,
    LIFECYCLE_MILESTONES,
    FRICTION_CATEGORIES,
    SEVERITY_LEVELS,
    UNMET_NEEDS
)
from golden_set import evaluate_golden_set
from scraper import ingest_touchpoints

app = FastAPI(
    title="Groww SIP Discovery Engine",
    description="Problem discovery and churn telemetry engine for first-time SIP investors.",
    version="2.0.0"
)

# ----------------------------------------------------------------------
# In-Memory Cache for High-Speed API Responses
# ----------------------------------------------------------------------
CACHE: Dict[str, Any] = {
    "df": None,
    "opportunities": None,
    "benchmark": None
}


def load_dataset() -> pd.DataFrame:
    """Loads and caches analyzed touchpoints."""
    if CACHE["df"] is not None:
        return CACHE["df"]

    file_path = "data/scraped_reviews.json"
    if not os.path.exists(file_path):
        raw_items = ingest_touchpoints(output_path=file_path)
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
            if not raw_items:
                raw_items = ingest_touchpoints(output_path=file_path)
        except Exception:
            raw_items = ingest_touchpoints(output_path=file_path)

    enriched = []
    for item in raw_items:
        text = item.get("raw_text", "")
        diag = classify_with_heuristic_engine(text)
        merged = dict(item)
        merged.update(diag)
        enriched.append(merged)

    df = pd.DataFrame(enriched)
    CACHE["df"] = df
    CACHE["opportunities"] = compute_opportunity_rankings(enriched)
    CACHE["benchmark"] = evaluate_golden_set()
    return df


# ----------------------------------------------------------------------
# API Models
# ----------------------------------------------------------------------
class DiagnoseRequest(BaseModel):
    text: str
    api_key: Optional[str] = None


# ----------------------------------------------------------------------
# API Endpoints
# ----------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Health check endpoint for Render."""
    return {"status": "ok", "service": "groww-sip-discovery"}


@app.get("/api/summary")
def get_summary():
    """Returns top-level KPI metrics and source breakdown."""
    df = load_dataset()
    total_touchpoints = len(df)
    sources = df["source"].value_counts().to_dict()
    outcomes = df["outcome"].value_counts().to_dict()
    churn_rate = round(float((df["outcome"] == "Stopped / cancelled").mean() * 100), 1)

    return {
        "total_touchpoints": total_touchpoints,
        "sources": sources,
        "outcomes": outcomes,
        "churn_rate_pct": churn_rate
    }


@app.get("/api/insights")
def get_insights():
    """Returns aggregated behavioral distribution data for frontend charts."""
    df = load_dataset()

    # 1. Stated start reasons (excluding 'Not stated' for charts)
    start_reasons = df[df["start_reason"] != "Not stated"]["start_reason"].value_counts().to_dict()

    # 2. Initial return expectations
    expectations = df[df["expectation"] != "Not stated"]["expectation"].value_counts().to_dict()

    # 3. Lifecycle milestones
    milestones = df["milestone"].value_counts().reindex(LIFECYCLE_MILESTONES).fillna(0).astype(int).to_dict()

    # 4. In-app confusions
    in_app_confusions = df["in_app_confusion"].value_counts().to_dict()

    # 5. Outside-app workarounds
    outside_actions = df[df["outside_action"] != "None mentioned"]["outside_action"].value_counts().to_dict()

    # 6. Continuers vs Droppers comparison
    df_comp = df[df["outcome"].isin(["Continued", "Stopped / cancelled"])].copy()
    ct = pd.crosstab(df_comp["unmet_need"], df_comp["outcome"], normalize="columns").mul(100).round(1)
    
    comparisons = []
    for need in ct.index:
        continued_pct = float(ct.loc[need].get("Continued", 0.0))
        stopped_pct = float(ct.loc[need].get("Stopped / cancelled", 0.0))
        gap = round(stopped_pct - continued_pct, 1)
        comparisons.append({
            "unmet_need": need,
            "continued_pct": continued_pct,
            "stopped_pct": stopped_pct,
            "gap_pp": gap
        })
    comparisons.sort(key=lambda x: x["gap_pp"], reverse=True)

    return {
        "start_reasons": start_reasons,
        "expectations": expectations,
        "milestones": milestones,
        "in_app_confusions": in_app_confusions,
        "outside_actions": outside_actions,
        "comparisons": comparisons
    }


@app.get("/api/opportunities")
def get_opportunities():
    """Returns mathematically calculated opportunity rankings."""
    if CACHE["opportunities"] is None:
        load_dataset()
    return CACHE["opportunities"]


@app.get("/api/benchmark")
def get_benchmark():
    """Returns AI Evidence Log, 20-item benchmark, and 3 documented correction cases."""
    if CACHE["benchmark"] is None:
        load_dataset()
    return CACHE["benchmark"]


@app.get("/api/verbatims")
def get_verbatims(
    source: Optional[str] = Query(None),
    milestone: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = 100
):
    """Returns filterable touchpoint verbatims."""
    df = load_dataset()
    filtered = df.copy()

    if source and source != "All":
        filtered = filtered[filtered["source"] == source]
    if milestone and milestone != "All":
        filtered = filtered[filtered["milestone"] == milestone]
    if severity and severity != "All":
        filtered = filtered[filtered["severity"] == severity]
    if search:
        search_lower = search.lower()
        filtered = filtered[filtered["raw_text"].str.lower().str.contains(search_lower, na=False)]

    records = filtered[["id", "source", "date", "rating", "milestone", "friction_category", "severity", "unmet_need", "raw_text"]].head(limit).to_dict(orient="records")
    return {
        "count": len(filtered),
        "results": records
    }


@app.post("/api/diagnose")
def run_diagnose(req: DiagnoseRequest):
    """Executes live diagnostic analysis on user-submitted text."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = analyze_review(req.text, api_key=req.api_key)
    return result


# ----------------------------------------------------------------------
# Serve Static Dashboard Frontend
# ----------------------------------------------------------------------
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8501))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
