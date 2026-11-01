"""
Groww SIP Discovery Engine - 100% Authentic Data Ingestion Pipeline (scraper.py)
---------------------------------------------------------------------------------
Collects, sanitizes, deduplicates, and normalizes 100% genuine, real-world user
touchpoints across public investor channels:
1. Google Play Store (Live reviews for Groww app via google-play-scraper)
2. Apple App Store (Live India customer reviews via official iTunes RSS feed)
3. TradingQ&A (Live investor forum conversations via Discourse API)
4. YouTube Personal Finance Comments (Live comments via YouTube Data API v3)

Strictly authentic: Zero mock templates, zero synthetic data expansion.
All touchpoints are scrubbed of PII (emails, phone numbers, account numbers, URLs).
"""

import os
import sys
import re
import json
import hashlib
import datetime
from typing import List, Dict, Any, Optional

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

try:
    from google_play_scraper import reviews, Sort
    PLAY_SCRAPER_AVAILABLE = True
except ImportError:
    PLAY_SCRAPER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ----------------------------------------------------------------------
# PII Scrubbing & Sanitization
# ----------------------------------------------------------------------
PHONE_REGEX = re.compile(r'(\+?91[\s\-]?)?[6-9]\d{9}\b|\b\d{10}\b')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE)
BANK_ACC_REGEX = re.compile(r'\b\d{11,16}\b')
URL_REGEX = re.compile(r'https?://\S+|www\.\S+')


def scrub_pii(text: str) -> str:
    """Removes sensitive personal identifiable information (PII) from raw text."""
    if not text or not isinstance(text, str):
        return ""
    text = EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
    text = PAN_REGEX.sub("[PAN_REDACTED]", text)
    text = PHONE_REGEX.sub("[PHONE_REDACTED]", text)
    text = BANK_ACC_REGEX.sub("[ACC_REDACTED]", text)
    text = URL_REGEX.sub("[LINK_REDACTED]", text)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_touchpoint_id(source: str, content: str) -> str:
    """Generates a deterministic unique ID based on source and content hash."""
    clean = re.sub(r'[^a-zA-Z0-9]', '', content.lower())
    short_hash = hashlib.md5(clean.encode('utf-8')).hexdigest()[:8]
    prefix = {
        "Google Play Store": "GP",
        "Apple App Store": "IOS",
        "TradingQ&A Forum": "TQNA",
        "YouTube Comments": "YT"
    }.get(source, "TP")
    return f"{prefix}-{short_hash}"


# Mutual fund and SIP relevant keywords to filter out generic stock/F&O day-trading reviews
SIP_KEYWORDS = [
    "sip", "mutual fund", "mf", "fund", "invest", "autopay", "mandate", "deduct", "bank",
    "nach", "installment", "penalty", "295", "590", "bounce", "return", "negative", "loss",
    "pause", "stop", "statement", "nav", "units", "cams", "kfintech", "iccl", "bse",
    "first time", "xirr", "kyc", "folio", "red", "dip", "skip", "start", "beginner"
]

EXCLUDE_KEYWORDS = [
    "option trading", "call option", "put option", "f&o", "futures and options",
    "crypto", "us stocks", "commodities", "intraday", "terminal"
]


# ----------------------------------------------------------------------
# 1. Google Play Store Scraper
# ----------------------------------------------------------------------
def scrape_play_store_reviews(package_name: str = "com.nextbillion.groww", max_fetch: int = 1000) -> List[Dict[str, Any]]:
    """Fetches real reviews from Google Play Store across NEWEST and MOST_RELEVANT sorts."""
    results: List[Dict[str, Any]] = []
    if not PLAY_SCRAPER_AVAILABLE:
        print("[!] google-play-scraper not installed; skipping Google Play.")
        return results

    print(f"[*] Fetching live Google Play Store reviews for {package_name}...")
    seen_ids = set()

    for sort_order in [Sort.NEWEST, Sort.MOST_RELEVANT]:
        try:
            raw_reviews, _ = reviews(
                package_name,
                lang='en',
                country='in',
                sort=sort_order,
                count=max_fetch
            )
            for item in raw_reviews:
                content = item.get("content", "")
                if not content or len(content) < 25:
                    continue

                content_lower = content.lower()
                if any(ex in content_lower for ex in EXCLUDE_KEYWORDS):
                    continue
                if not any(kw in content_lower for kw in SIP_KEYWORDS):
                    continue

                cleaned_content = scrub_pii(content)
                tp_id = generate_touchpoint_id("Google Play Store", cleaned_content)
                if tp_id in seen_ids:
                    continue
                seen_ids.add(tp_id)

                date_val = item.get("at", datetime.datetime.now())
                date_str = date_val.strftime("%Y-%m-%d") if hasattr(date_val, "strftime") else str(date_val)[:10]

                results.append({
                    "id": tp_id,
                    "source": "Google Play Store",
                    "date": date_str,
                    "rating": item.get("score"),
                    "raw_text": cleaned_content
                })
        except Exception as e:
            print(f"[!] Google Play fetch error ({sort_order}): {e}")

    print(f"[OK] Extracted {len(results)} authentic Google Play Store reviews.")
    return results


# ----------------------------------------------------------------------
# 2. Apple App Store Scraper (Official iTunes Customer Reviews RSS)
# ----------------------------------------------------------------------
def scrape_app_store_reviews(app_id: str = "1404871703", max_pages: int = 10) -> List[Dict[str, Any]]:
    """Fetches Groww iOS customer reviews from the official Apple iTunes RSS JSON feed (India storefront)."""
    results: List[Dict[str, Any]] = []
    if not REQUESTS_AVAILABLE:
        return results

    print("[*] Fetching live Apple App Store reviews for Groww iOS...")
    seen_ids = set()

    for page in range(1, max_pages + 1):
        url = f"https://itunes.apple.com/in/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        try:
            resp = requests.get(url, timeout=12)
            if resp.status_code != 200:
                break
            entries = resp.json().get("feed", {}).get("entry", [])
            for entry in entries:
                if "content" not in entry or "im:rating" not in entry:
                    continue

                title = entry.get("title", {}).get("label", "")
                body = entry.get("content", {}).get("label", "")
                full_text = f"{title}. {body}".strip()
                if len(full_text) < 25:
                    continue

                full_lower = full_text.lower()
                if any(ex in full_lower for ex in EXCLUDE_KEYWORDS):
                    continue
                if not any(kw in full_lower for kw in SIP_KEYWORDS):
                    continue

                cleaned_content = scrub_pii(full_text)
                tp_id = generate_touchpoint_id("Apple App Store", cleaned_content)
                if tp_id in seen_ids:
                    continue
                seen_ids.add(tp_id)

                rating = int(entry.get("im:rating", {}).get("label", 3))
                date_str = entry.get("updated", {}).get("label", "")[:10]

                results.append({
                    "id": tp_id,
                    "source": "Apple App Store",
                    "date": date_str,
                    "rating": rating,
                    "raw_text": cleaned_content
                })
        except Exception as e:
            print(f"[!] App Store page {page} fetch error: {e}")
            break

    print(f"[OK] Extracted {len(results)} authentic Apple App Store reviews.")
    return results


# ----------------------------------------------------------------------
# 3. TradingQ&A Investor Community Forum Scraper
# ----------------------------------------------------------------------
def scrape_tradingqna_forum() -> List[Dict[str, Any]]:
    """
    Fetches real public community discussions from TradingQ&A (India's leading retail investing Q&A forum).
    Uses public Discourse search JSON API without requiring authentication.
    """
    results: List[Dict[str, Any]] = []
    if not REQUESTS_AVAILABLE:
        return results

    print("[*] Fetching live investor discussions from TradingQ&A Forum...")
    queries = [
        "Groww SIP", "first SIP", "autopay failed", "SIP pause",
        "SIP mandate bounce", "SIP loss red", "mutual fund deduction",
        "first time investor SIP"
    ]
    seen_ids = set()

    for q in queries:
        url = f"https://tradingqna.com/search.json?q={requests.utils.quote(q)}"
        try:
            resp = requests.get(url, timeout=12)
            if resp.status_code == 200:
                posts = resp.json().get("posts", [])
                for p in posts:
                    blurb = p.get("blurb", "")
                    if len(blurb) < 30:
                        continue
                    cleaned = scrub_pii(blurb)
                    tp_id = generate_touchpoint_id("TradingQ&A Forum", cleaned)
                    if tp_id in seen_ids:
                        continue
                    seen_ids.add(tp_id)

                    created_at = p.get("created_at", "")[:10]
                    results.append({
                        "id": tp_id,
                        "source": "TradingQ&A Forum",
                        "date": created_at or "2024-01-01",
                        "rating": None,
                        "raw_text": cleaned
                    })
        except Exception as e:
            print(f"[!] TradingQ&A query '{q}' error: {e}")

    print(f"[OK] Extracted {len(results)} authentic TradingQ&A discussions.")
    return results


# ----------------------------------------------------------------------
# 4. YouTube Comments on Personal Finance SIP Videos (Live via Data API v3)
# ----------------------------------------------------------------------
def scrape_youtube_comments(
    queries: Optional[List[str]] = None,
    videos_per_query: int = 4,
    comments_per_video: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetches top-level comments from popular personal finance videos about starting/stopping SIPs in India.
    Requires YOUTUBE_API_KEY set in .env or environment.
    """
    results: List[Dict[str, Any]] = []
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("[i] YOUTUBE_API_KEY not found in environment/.env; skipping live YouTube comment fetch.")
        return results

    if not REQUESTS_AVAILABLE:
        return results

    print("[*] Fetching live YouTube comments on Indian personal finance videos...")
    queries = queries or [
        "SIP for beginners India Groww",
        "stopped my SIP mutual fund mistakes",
        "Groww SIP autopay problem",
        "why mutual fund SIP loss"
    ]
    base_url = "https://www.googleapis.com/youtube/v3"
    seen_ids = set()

    for query in queries:
        try:
            search_resp = requests.get(
                f"{base_url}/search",
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": videos_per_query,
                    "regionCode": "IN",
                    "relevanceLanguage": "en",
                    "key": api_key
                },
                timeout=12
            )
            if search_resp.status_code != 200:
                print(f"[!] YouTube search error: {search_resp.status_code} - {search_resp.text[:100]}")
                continue

            items = search_resp.json().get("items", [])
            for video_item in items:
                video_id = video_item.get("id", {}).get("videoId")
                if not video_id:
                    continue

                comments_resp = requests.get(
                    f"{base_url}/commentThreads",
                    params={
                        "part": "snippet",
                        "videoId": video_id,
                        "maxResults": comments_per_video,
                        "textFormat": "plainText",
                        "key": api_key
                    },
                    timeout=12
                )
                if comments_resp.status_code != 200:
                    continue

                comment_items = comments_resp.json().get("items", [])
                for c_item in comment_items:
                    snippet = c_item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                    raw_text = snippet.get("textDisplay", "")
                    if len(raw_text) < 30:
                        continue

                    # Filter for relevance
                    text_lower = raw_text.lower()
                    if not any(kw in text_lower for kw in SIP_KEYWORDS):
                        continue

                    cleaned = scrub_pii(raw_text)
                    tp_id = generate_touchpoint_id("YouTube Comments", cleaned)
                    if tp_id in seen_ids:
                        continue
                    seen_ids.add(tp_id)

                    pub_date = snippet.get("publishedAt", "")[:10]
                    results.append({
                        "id": tp_id,
                        "source": "YouTube Comments",
                        "date": pub_date,
                        "rating": None,
                        "raw_text": cleaned
                    })
        except Exception as e:
            print(f"[!] YouTube fetch error for '{query}': {e}")

    print(f"[OK] Extracted {len(results)} authentic YouTube comments.")
    return results


# ----------------------------------------------------------------------
# Master Ingestion Function (100% Genuine Data Only)
# ----------------------------------------------------------------------
def ingest_touchpoints(output_path: str = "data/scraped_reviews.json") -> List[Dict[str, Any]]:
    """
    Master ingestion: gathers only authentic data from Google Play Store,
    Apple App Store, TradingQ&A, and YouTube. Zero synthetic mock data.
    """
    all_touchpoints: List[Dict[str, Any]] = []
    seen_texts = set()

    # 1. Google Play Store reviews
    for item in scrape_play_store_reviews():
        norm = re.sub(r'\W+', '', item['raw_text'].lower())
        if norm not in seen_texts:
            seen_texts.add(norm)
            all_touchpoints.append(item)

    # 2. Apple App Store reviews
    for item in scrape_app_store_reviews():
        norm = re.sub(r'\W+', '', item['raw_text'].lower())
        if norm not in seen_texts:
            seen_texts.add(norm)
            all_touchpoints.append(item)

    # 3. TradingQ&A Community Forum posts
    for item in scrape_tradingqna_forum():
        norm = re.sub(r'\W+', '', item['raw_text'].lower())
        if norm not in seen_texts:
            seen_texts.add(norm)
            all_touchpoints.append(item)

    # 4. YouTube Comments (if YOUTUBE_API_KEY provided)
    for item in scrape_youtube_comments():
        norm = re.sub(r'\W+', '', item['raw_text'].lower())
        if norm not in seen_texts:
            seen_texts.add(norm)
            all_touchpoints.append(item)

    # Deduplicate strictly by ID
    deduped: List[Dict[str, Any]] = []
    seen_ids = set()
    for item in all_touchpoints:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            deduped.append(item)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Ingested {len(deduped)} 100% authentic touchpoints saved to '{output_path}'.")
    return deduped


if __name__ == "__main__":
    ingest_touchpoints()
