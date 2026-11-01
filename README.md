# 🌱 Groww SIP Discovery Engine
### Mutual Funds Growth & Retention Pod — Problem Discovery & Churn Telemetry

**Strategic Objective:** Discover why first-time mutual fund investors pause, reduce, or stop their SIPs between Month 1 and Month 12, and diagnose high-leverage product opportunities to increase **12-Month SIP Retention** without recommending specific funds or using manipulative FOMO nudges.

---

## 📌 Strategic Goals & Questions Addressed

This engine is engineered specifically to answer the core behavioral discovery questions:
1. **Why do people start a SIP, and what do they expect to happen?**
   - Deconstructs stated entry motives (wealth creation, small start, tax saving) and uncovers unanchored expectations (FD-mindset expecting guaranteed gains vs equity reality).
2. **What changes in their behavior in the months after starting?**
   - Maps behavioral progression from Month 1 (mandate setup) to Month 2-3 (T+2 NAV settlement), Month 4-6 (first market correction panic), and Month 7-12 (cashflow/salary date mismatch).
3. **What leads investors to pause, reduce, or stop a SIP?**
   - Identifies root triggers: unexpected bank ECS bounce penalties (₹295–₹590), negative XIRR panic, and inability to pause without deleting the mandate.
4. **What do investors check, and how often, once they have started?**
   - Categorizes checking behavior (daily market tracking, alert-driven checking, occasional review) and highlights what alarms them inside the app.
5. **What confuses or worries them inside the app?**
   - Diagnoses in-app confusion points: statutory BSE/ICCL alerts, T+2 order-in-progress opacity, and missing 1-tap pause options.
6. **What do they do outside the app when they feel unsure?**
   - Uncovers off-platform workarounds: NetBanking mandate cancellations, cross-checking on CAMS/KFintech, moving capital back to Fixed Deposits, and seeking peer advice.
7. **What separates investors who continue from those who quietly drop off?**
   - Directly compares friction distribution between continuing investors and those who permanently churned.
8. **Quantified Opportunity Sizing:**
   - Sizing is computed mathematically from the empirical corpus using prevalence, 95% Wilson confidence intervals, and stop-rate correlation lift.
9. **AI Evidence Log & Quality Validation:**
   - Validates classification accuracy against a 20-case Human Ground Truth benchmark and documents 3 complex fintech edge cases where naive AI misclassified and was corrected.

---

## 🏗️ System Architecture

```text
groww_sip_discovery/
├── requirements.txt         # Clean, lightweight dependencies (fastapi, uvicorn, etc.)
├── .env                     # API key configuration (GEMINI_API_KEY, YOUTUBE_API_KEY)
├── scraper.py               # 100% genuine data collection (Google Play, App Store RSS, TradingQ&A, YouTube)
├── analyzer.py              # Behavioral evaluation pipeline (Gemini Flash + Offline Deterministic Engine)
├── golden_set.py            # AI Evidence Log & 20-item Ground Truth Benchmark with 3 correction cases
├── server.py                # High-performance FastAPI server (<40MB RAM, sub-second boot)
├── static/                  # Modern, clean frontend (Groww mint aesthetic)
│   ├── index.html           # 4-Tab Executive Dashboard (Semantic HTML5)
│   ├── style.css            # Vanilla CSS design system tokens
│   └── app.js               # Client-side Chart.js visualizations & live diagnostic harness
├── data/
│   ├── golden_set.json      # Curated 20 benchmark cases with ground truth & comparison metrics
│   └── scraped_reviews.json # 920+ authentic, deduplicated, and PII-sanitized investor verbatims
├── render.yaml              # 1-Click Render.com deployment blueprint
└── README.md                # System documentation & deployment guide
```

---

## 📡 100% Authentic Data Channels

| Channel | Method / Protocol | Authentication | Volume |
| :--- | :--- | :--- | :--- |
| **Google Play Store** | Live reviews for Groww app via `google-play-scraper` (Newest + Relevant) | Zero auth | 540+ reviews |
| **Apple App Store** | Live India storefront customer reviews via official iTunes RSS JSON feed | Zero auth | 110+ reviews |
| **TradingQ&A Forum** | Live investor conversations via Discourse public search API | Zero auth | 260+ posts |
| **YouTube Comments** | Live top comments on personal finance SIP videos via YouTube Data API v3 | `YOUTUBE_API_KEY` | Optional |

*Note: All touchpoints are scrubbed of PII (emails, phone numbers, PAN cards, account numbers).*

---

## 🛡️ Free-Tier & Zero-Cost Architecture

- **Data Ingestion:** 100% free unauthenticated public feeds (Play Store, App Store RSS, TradingQ&A).
- **AI / LLM Layer:** Google Gemini 2.5/1.5 Flash via `google-genai` SDK. Automatically falls back to a deterministic domain heuristic engine if `GEMINI_API_KEY` is not configured.
- **Backend API:** FastAPI + Uvicorn (Python). Runs in **~35MB RAM** (eliminates Render OOM crashes).
- **Frontend Dashboard:** Modern Vanilla HTML5, CSS3, and Chart.js.

---

## ⚖️ AI Evidence Log & Golden Benchmark (`golden_set.py`)

A curated set of **20 real-world fintech edge cases** evaluated side-by-side (Human Ground Truth vs AI Pipeline):
- **Milestone Agreement Rate:** **90.0%**
- **Friction Category Agreement Rate:** **90.0%**
- **Severity Agreement Rate:** **80.0%**
- **Strict Overall Agreement:** **75.0%**

### 3 Documented Rejection & Correction Cases:
1. **Case 1 (GS-16): Bank-Level NACH Mandate Rejection vs In-App Bug**
   - *Review:* *"Groww deducted ₹295 penalty from my SBI account for no reason! Worst app, full of software bugs, deleting it right now!"*
   - *Naive AI Output:* `Product / UI Friction` (Misattributed bank penalty to Groww in-app bug).
   - *Human Ground Truth:* `Operational / Autopay Friction` (NPCI ECS return penalty levied by SBI due to insufficient balance on debit date).
   - *PM Takeaway:* Groww must send a 48h Pre-Debit Balance Warning and offer a 1-tap zero-penalty skip before presenting the mandate to the bank.
2. **Case 2 (GS-11): Short-Term Market Volatility (Negative XIRR) vs Fraud / Theft**
   - *Review:* *"I invested ₹5000 in monthly SIP for 4 months, total ₹20,000. Now portfolio shows ₹19,100. Groww has stolen my ₹900! Equity is a scam. Stopped all SIPs."*
   - *Naive AI Output:* `Operational / Autopay Friction` (Interpreted "stolen" literally as an accounting discrepancy).
   - *Human Ground Truth:* `Cognitive / Expectation Gap` (Interim 4.5% equity correction misinterpreted as theft by investor with an FD mindset).
   - *PM Takeaway:* Deploy "SIP Volatility Shield" with 3-year historical drawdown recovery bands to anchor investor patience.
3. **Case 3 (GS-07): Regulatory Clearing House (ICCL/BSE) SMS vs Phishing Scam**
   - *Review:* *"Received an SMS from ICCL saying mandate approved for ₹5000 debit. I never registered on ICCL, only on Groww! Thought my bank was hacked. Cancelled mandate immediately from NetBanking."*
   - *Naive AI Output:* `Product / UI Friction` (Classified as minor notification confusion).
   - *Human Ground Truth:* `Operational / Autopay Friction` (Statutory clearing SMS created scam fear, leading to fatal mandate revocation).
   - *PM Takeaway:* Set expectations during Month 1 onboarding: *"You will receive official regulatory SMS from ICCL/BSE — this is SEBI-mandated clearing, not a scam."*

---

## 🚀 Quickstart Guide (Local Execution)

### 1. Prerequisites:
Python 3.10+ installed.

### 2. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys (Optional):
Open `.env` and paste your keys:
```env
GEMINI_API_KEY=your-gemini-api-key
YOUTUBE_API_KEY=your-youtube-api-key
```
*(The engine runs completely offline with full accuracy if keys are omitted!)*

### 4. Run Data Ingestion (Optional - dataset already included):
```bash
python scraper.py
```

### 5. Launch the Executive Dashboard:
```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your browser.

---

## 🌐 Deploying to Render (Free Tier)

This repository includes a pre-configured `render.yaml` ready for 1-click deployment on [Render.com](https://render.com).

### Step-by-Step Instructions:
1. **Commit and push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Migrate to lightweight FastAPI + HTML5 dashboard"
   git push origin main
   ```
2. **Log into [Render.com](https://dashboard.render.com):**
   - Click **"New +"** and choose **"Web Service"**.
   - Connect your GitHub repository: `TenaciousSwan/Groww-sip-discovery`.
3. **Verify Settings (Auto-detected via `render.yaml`):**
   - **Name:** `groww-sip-discovery`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. **Environment Variables (Optional):**
   - Under **Environment Variables**, add:
     - `GEMINI_API_KEY`: *(your Gemini key)*
     - `YOUTUBE_API_KEY`: *(your YouTube key)*
     - `PYTHON_VERSION`: `3.10.12`
5. **Click "Create Web Service":**
   Render will build the application in ~30 seconds and provide a permanent public HTTPS URL (e.g., `https://groww-sip-discovery.onrender.com`).


