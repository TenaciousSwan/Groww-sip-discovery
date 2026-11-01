"""
Groww SIP Retention Radar - AI Evidence Log & Ground Truth Benchmark (golden_set.py)
-------------------------------------------------------------------------------------
Manages a curated Golden Set of exactly 20 items representing diverse real-world edge cases.
Provides a side-by-side benchmark comparison between Human Ground Truth vs AI Pipeline.
Calculates agreement rates, confusion metrics, and details 3 documented correction cases
with deep PM rationale for Groww Growth & Retention diagnostics.
"""

import os
import sys
import json
from typing import List, Dict, Any, Tuple, Optional
from analyzer import analyze_review, LIFECYCLE_MILESTONES, FRICTION_CATEGORIES, SEVERITY_LEVELS

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# ----------------------------------------------------------------------
# Exactly 20 Curated Golden Set Benchmark Cases (Human Ground Truth)
# ----------------------------------------------------------------------
GOLDEN_SET_ITEMS: List[Dict[str, Any]] = [
    # --- Month 1: Onboarding / Setup (Items 1-5) ---
    {
        "id": "GS-01",
        "raw_text": "I set up my first SIP of ₹1000 in Parag Parikh Flexi Cap. When approving the mandate in Google Pay, it showed 'Max debit limit: ₹1,00,000'. I panicked thinking Groww will deduct 1 lakh from my savings account! Declined the mandate immediately and deleted the app.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "NPCI UPI autopay statutory ceiling of ₹1,00,000 mistaken for actual recurring deduction amount, inducing scam fear.",
            "user_workaround": "Declined the UPI mandate in Google Pay and deleted the app."
        },
        "context_tags": ["UPI Autopay", "NPCI Limit Panic", "Onboarding", "Google Pay"]
    },
    {
        "id": "GS-02",
        "raw_text": "I started my first SIP on Groww with ₹1500. I paid ₹1500 using UPI on 3rd Jan, but then on 5th Jan another ₹1500 was deducted automatically from my bank! That is a double deduction. Groww support said first was initial order and second was autopay. Cancelled the autopay immediately.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Overlapping execution of first manual order and scheduled automated installment caused double debit panic.",
            "user_workaround": "Cancelled the automated mandate in NetBanking."
        },
        "context_tags": ["Double Deduction", "First Month", "Mandate Timing", "Support"]
    },
    {
        "id": "GS-03",
        "raw_text": "Trying to link my Canara Bank account for e-NACH mandate. It has been 9 days and it still shows 'Mandate Registration in Progress'. I called bank and they said no request received from Groww. Now Groww says retry. Too much friction for just a ₹500 investment.",
        "source": "Reddit (r/mutualfunds)",
        "human_ground_truth": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Operational / Autopay Friction",
            "severity": "High",
            "primary_behavioral_driver": "Prolonged bank-broker synchronization lag during e-NACH registration created high setup fatigue.",
            "user_workaround": "Abandoned the setup flow before second installment."
        },
        "context_tags": ["e-NACH", "Canara Bank", "Setup Friction", "Verification Lag"]
    },
    {
        "id": "GS-04",
        "raw_text": "The signature upload step during onboarding kept rejecting my clear photo 4 times saying 'Signature does not match PAN'. The camera crop box in the app is poorly designed. Eventually managed to upload after 20 minutes.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Product / UI Friction",
            "severity": "Low",
            "primary_behavioral_driver": "Clunky in-app photo cropping tool caused minor onboarding frustration without halting the investment.",
            "user_workaround": "Retried photo upload multiple times until approved."
        },
        "context_tags": ["KYC", "Signature Upload", "UI Friction", "Onboarding"]
    },
    {
        "id": "GS-05",
        "raw_text": "I set up my first SIP in Nippon India Small Cap Fund on Groww. But when the mandate authorization screen came, it displayed 'BSE StAR MF / ICCL' as merchant instead of Groww. As a beginner, I was confused whether my money is going to Groww or someone else.",
        "source": "YouTube / Community",
        "human_ground_truth": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "Medium",
            "primary_behavioral_driver": "Lack of expectation setting around regulatory clearing house intermediaries (BSE/ICCL) induced momentary hesitation.",
            "user_workaround": "Hesitated and consulted online forums before completing setup."
        },
        "context_tags": ["Merchant Name", "BSE StAR MF", "ICCL", "Beginner Confusion"]
    },

    # --- Month 2-3: First Statements & Friction (Items 6-10) ---
    {
        "id": "GS-06",
        "raw_text": "Money got deducted from my Axis bank account on Friday 2nd Feb for my monthly SIP. But throughout Saturday, Sunday, and Monday my Groww portfolio showed ₹0 invested and order in progress! I thought my money was lost in transit. T+2 settlement should be clearly explained to newcomers.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 2-3: First Statements & Friction",
            "friction_category": "Product / UI Friction",
            "severity": "High",
            "primary_behavioral_driver": "Weekend settlement delay (T+2 business days) combined with zero in-app progress tracking triggered severe loss anxiety.",
            "user_workaround": "Emailed customer support and raised anxious queries on social media."
        },
        "context_tags": ["T+2 Settlement", "Axis Bank", "Order in Progress", "NAV Delay"]
    },
    {
        "id": "GS-07",
        "raw_text": "Received an SMS from ICCL saying mandate approved for ₹5000 debit. I never registered on ICCL, only on Groww! Thought my bank was hacked by fraudsters. Logged into NetBanking and cancelled the mandate immediately.",
        "source": "Reddit (r/mutualfunds)",
        "human_ground_truth": {
            "milestone": "Month 2-3: First Statements & Friction",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Regulatory statutory settlement SMS from Indian Clearing Corporation Limited created fraud alarm, triggering user to revoke the banking mandate.",
            "user_workaround": "Logged into NetBanking and cancelled the bank mandate directly."
        },
        "context_tags": ["ICCL SMS", "Scam Fear", "Mandate Revocation", "Correction Case 3"]
    },
    {
        "id": "GS-08",
        "raw_text": "Got a Consolidated Account Statement (CAS) email from CAMS. It listed my investments with folio numbers under Mirae Asset Mutual Fund with no mention of Groww anywhere. Thought my Groww account had disconnected or data was leaked. Very confusing for non-tech users.",
        "source": "Reddit (r/IndiaInvestments)",
        "human_ground_truth": {
            "milestone": "Month 2-3: First Statements & Friction",
            "friction_category": "Product / UI Friction",
            "severity": "Medium",
            "primary_behavioral_driver": "Disconnect between broker front-end and RTA back-end reporting confused investor about custody of assets.",
            "user_workaround": "Cross-checked CAMS portal manually to verify holdings."
        },
        "context_tags": ["CAMS", "CAS Statement", "Folio Confusion", "Mirae Asset"]
    },
    {
        "id": "GS-09",
        "raw_text": "My SIP deduction date was 10th of March. On 10th Nifty was at 22,000. But the NAV allotted to me in Groww was dated 12th March when Nifty jumped to 22,350! I got fewer units at a higher price because Groww delayed submitting my order to the AMC. Paused my SIP.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 2-3: First Statements & Friction",
            "friction_category": "Product / UI Friction",
            "severity": "Medium",
            "primary_behavioral_driver": "NAV realization cutoff lag resulted in allocation at unfavorable prices, eroding investor trust in broker execution.",
            "user_workaround": "Paused the monthly SIP."
        },
        "context_tags": ["NAV Allotment", "Cutoff Timing", "Fewer Units", "Trust Deficit"]
    },
    {
        "id": "GS-10",
        "raw_text": "I downloaded the account statement PDF after 2 months. Found deductions for stamp duty (0.005%) and Total Expense Ratio (TER). When I started SIP, Groww advertised 'Zero Commission Mutual Funds'. Why are these hidden charges being taken? Stopped my investment.",
        "source": "YouTube / Community",
        "human_ground_truth": {
            "milestone": "Month 2-3: First Statements & Friction",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "High",
            "primary_behavioral_driver": "Failure to distinguish between statutory government stamp duty / AMC expense ratio and zero broker commission created perception of hidden fees.",
            "user_workaround": "Stopped monthly investment."
        },
        "context_tags": ["Stamp Duty", "TER", "Zero Commission", "Hidden Charges"]
    },

    # --- Month 4-6: Market Dip / Downturn (Items 11-15) ---
    {
        "id": "GS-11",
        "raw_text": "I invested ₹5000 in monthly SIP for 4 months, total ₹20,000. Now portfolio shows ₹19,100. Groww has stolen my ₹900! Equity is a scam and broker is cheating customers. Stopped all SIPs.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Investor psychological panic caused by unanchored expectations and FD-mindset where market dip is perceived as fraudulent theft.",
            "user_workaround": "Stopped all active SIPs and exited mutual fund investing."
        },
        "context_tags": ["Market Correction", "Stolen Accusation", "FD Mindset", "Correction Case 2"]
    },
    {
        "id": "GS-12",
        "raw_text": "Started SIP in Quant Small Cap fund 5 months ago. Small cap index took a beating this month and my returns show -18% XIRR! Seeing my hard earned ₹15,000 in bright red color caused so much anxiety. Cancelled the SIP immediately and put remaining funds in PPF.",
        "source": "Reddit (r/mutualfunds)",
        "human_ground_truth": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Extreme loss aversion triggered by small-cap volatility and annualized negative XIRR visualization.",
            "user_workaround": "Terminated SIP and reallocated capital to government PPF."
        },
        "context_tags": ["Small Cap", "XIRR Panic", "PPF", "Red Portfolio"]
    },
    {
        "id": "GS-13",
        "raw_text": "Doing ₹3000 SIP for 5 months. Total invested ₹15,000, current value ₹14,800. In my SBI Fixed Deposit I would have earned guaranteed 7% interest without any stress. Equity mutual funds are useless for middle class people. Paused SIP indefinitely.",
        "source": "YouTube / Community",
        "human_ground_truth": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Mental accounting comparison against risk-free guaranteed fixed deposit returns during interim market drawdown.",
            "user_workaround": "Paused SIP indefinitely and shifted savings back to bank FD."
        },
        "context_tags": ["FD Comparison", "SBI", "Guaranteed Returns", "Indefinite Pause"]
    },
    {
        "id": "GS-14",
        "raw_text": "In Month 5 my portfolio dropped 4%. I decided to withdraw some money, but then the app warned me about a 1% exit load and short-term capital gains tax. I felt trapped. Why didn't Groww explain exit loads clearly upfront when I started the SIP?",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "High",
            "primary_behavioral_driver": "Lack of upfront awareness regarding AMC exit loads during downturns triggered feeling of capital lock-in.",
            "user_workaround": "Stopped further SIP installments to avoid adding capital."
        },
        "context_tags": ["Exit Load", "Lock-in", "STCG", "Month 5 Drop"]
    },
    {
        "id": "GS-15",
        "raw_text": "Market dipped slightly in my 4th month of investing in Nifty 50. My portfolio was down ₹250. Is this normal? App shows a red banner every time market drops, which is a bit scary, but I plan to keep investing.",
        "source": "Reddit (r/mutualfunds)",
        "human_ground_truth": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "Low",
            "primary_behavioral_driver": "Mild anxiety provoked by alarming red visual indicators during minor market volatility, but habit remains intact.",
            "user_workaround": "Sought reassurance in community forums and continued SIP."
        },
        "context_tags": ["Mild Volatility", "Red Banner", "Community Reassurance"]
    },

    # --- Month 7-12: Disengagement / Lapse (Items 16-20) ---
    {
        "id": "GS-16",
        "raw_text": "Groww deducted ₹295 penalty from my SBI account for no reason! Worst app, full of software bugs, deleting it right now!",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 7-12: Disengagement/Lapse",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Bank-level ECS mandate bounce return charge levied by SBI due to insufficient balance, misattributed to the broker.",
            "user_workaround": "Uninstalled app and revoked mandate to stop recurring penalties."
        },
        "context_tags": ["SBI Penalty", "₹295 Fee", "Bounce", "Correction Case 1"]
    },
    {
        "id": "GS-17",
        "raw_text": "I had a sudden family medical expense in Month 8 and wanted to pause my ₹5000 SIP for 2 months. In Groww app, there is no pause option for my fund! The only button is 'Cancel SIP'. Once cancelled, I have to re-do bank mandate. So frustrating, I just cancelled and won't restart.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 7-12: Disengagement/Lapse",
            "friction_category": "Product / UI Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Product architecture limitation that conflates temporary cashflow pause with irreversible mandate termination.",
            "user_workaround": "Cancelled the SIP permanently and declined to restart."
        },
        "context_tags": ["Missing Pause Button", "Cancel SIP", "Medical Expense", "Month 8"]
    },
    {
        "id": "GS-18",
        "raw_text": "During Diwali month, my salary account had low balance. Groww tried to debit my ₹2000 SIP twice in 3 days. HDFC bank slapped me with ₹590 ECS bounce charges! I lost ₹590 just for trying to save ₹2000. Revoked the mandate from HDFC netbanking immediately.",
        "source": "Reddit (r/mutualfunds)",
        "human_ground_truth": {
            "milestone": "Month 7-12: Disengagement/Lapse",
            "friction_category": "Liquidity / Cashflow Mismatch",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Repeated mandate retries during seasonal cash crunch triggered punitive bank bounce fines exceeding the installment value.",
            "user_workaround": "Revoked the mandate via HDFC NetBanking."
        },
        "context_tags": ["Diwali Crunch", "HDFC ₹590", "Mandate Retry", "Revocation"]
    },
    {
        "id": "GS-19",
        "raw_text": "I switched jobs in Month 9 and my new employer credits salary on the 10th instead of the 1st. I tried changing my SIP date on Groww, but the app says date cannot be modified for active SIP! I had to delete the SIP. Creating a new one failed twice. Gave up.",
        "source": "Reddit (r/IndiaInvestments)",
        "human_ground_truth": {
            "milestone": "Month 7-12: Disengagement/Lapse",
            "friction_category": "Product / UI Friction",
            "severity": "High",
            "primary_behavioral_driver": "Inability to dynamically update installment debit date to match altered corporate payroll schedules forced destructive cancellation.",
            "user_workaround": "Deleted SIP and abandoned re-registration."
        },
        "context_tags": ["SIP Date Change", "Salary Shift", "Rigid Workflow", "Month 9"]
    },
    {
        "id": "GS-20",
        "raw_text": "I set up a 10% annual step-up SIP when starting. In Month 12, deduction increased from ₹5000 to ₹5500. I had forgotten about it and my balance was ₹5200. The mandate bounced and bank charged ₹295. Too many surprise penalties. Stopped all SIPs.",
        "source": "Google Play Store",
        "human_ground_truth": {
            "milestone": "Month 7-12: Disengagement/Lapse",
            "friction_category": "Liquidity / Cashflow Mismatch",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Unheralded automatic step-up debit increase breached account balance threshold, resulting in punitive bank penalty.",
            "user_workaround": "Stopped all active SIPs."
        },
        "context_tags": ["Step-up SIP", "Month 12", "Surprise Debit", "Bank Penalty"]
    }
]


# ----------------------------------------------------------------------
# 3 Explicit Documented Rejection & Correction Cases
# ----------------------------------------------------------------------
DOCUMENTED_CORRECTION_CASES = [
    {
        "case_id": "CORR-01",
        "golden_id": "GS-16",
        "title": "Bank-Level NACH Mandate Rejection vs In-App Groww Software Bug",
        "raw_text": "Groww deducted ₹295 penalty from my SBI account for no reason! Worst app, full of software bugs, deleting it right now!",
        "naive_ai_classification": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Product / UI Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "User encountered in-app billing software bugs and uninstalled the app."
        },
        "human_ground_truth": {
            "milestone": "Month 7-12: Disengagement/Lapse",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Bank-level ECS mandate bounce return charge levied by SBI due to insufficient balance, misattributed to the broker."
        },
        "pm_rationale": "The deduction of ₹295 is an exact NPCI NACH clearing return penalty charged by State Bank of India when an automated mandate debit fails due to insufficient funds on the scheduled debit date. Naive LLMs misclassify this as 'Product / UI Friction' because the user explicitly says 'Groww deducted... full of software bugs'. A PM must realize this is an external banking infrastructure penalty misattributed to the fintech app. Groww must introduce a Mandate Pre-Debit Warning (T-48h) via push/SMS and a 1-Tap Instant Skip to ensure no bank mandate is presented when balance is insufficient."
    },
    {
        "case_id": "CORR-02",
        "golden_id": "GS-11",
        "title": "Short-Term Market Volatility (Negative XIRR) vs Fraud / Financial Theft",
        "raw_text": "I invested ₹5000 in monthly SIP for 4 months, total ₹20,000. Now portfolio shows ₹19,100. Groww has stolen my ₹900! Equity is a scam and broker is cheating customers. Stopped all SIPs.",
        "naive_ai_classification": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Account balance discrepancy and missing ₹900 fund deduction."
        },
        "human_ground_truth": {
            "milestone": "Month 4-6: Market Dip/Downturn",
            "friction_category": "Cognitive / Expectation Gap",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Investor psychological panic caused by unanchored expectations and FD-mindset where market dip is perceived as fraudulent theft."
        },
        "pm_rationale": "The user experienced a standard 4.5% equity market correction in Month 4. The naive AI took the word 'stolen' literally and classified it as an operational balance accounting error. In reality, first-time Indian investors transition from fixed deposits where principal never drops; when equity dips into the red, loss aversion triggers panic and accusations of fraud. Groww's growth team cannot offer fund advice, but CAN build an 'Expectation & Drawdown Recovery Shield' showing 3-year rolling recovery bands for the Nifty 50 to anchor patience."
    },
    {
        "case_id": "CORR-03",
        "golden_id": "GS-07",
        "title": "Regulatory Clearing House (ICCL/BSE StAR) SMS vs Phishing Scam",
        "raw_text": "Received an SMS from ICCL saying mandate approved for ₹5000 debit. I never registered on ICCL, only on Groww! Thought my bank was hacked by fraudsters. Logged into NetBanking and cancelled the mandate immediately.",
        "naive_ai_classification": {
            "milestone": "Month 1: Onboarding/Setup",
            "friction_category": "Product / UI Friction",
            "severity": "High",
            "primary_behavioral_driver": "User confused by notification settings and unclear account status."
        },
        "human_ground_truth": {
            "milestone": "Month 2-3: First Statements & Friction",
            "friction_category": "Operational / Autopay Friction",
            "severity": "Fatal (Causes immediate cancellation)",
            "primary_behavioral_driver": "Regulatory statutory settlement SMS from Indian Clearing Corporation Limited created fraud alarm, triggering user to revoke the banking mandate."
        },
        "pm_rationale": "Under SEBI mutual fund regulations, stock brokers route transactions through clearing corporations (ICCL or BSE StAR MF). These entities send statutory SMS alerts directly to the investor's mobile number. First-time investors who have only heard of 'Groww' naturally suspect unauthorized third-party phishing. The naive LLM classified this as minor UI friction, missing the fatal operational consequence (user revoked the e-mandate in NetBanking). The PM fix is Proactive Onboarding Messaging in Month 1: 'You will receive statutory SMS from ICCL/BSE — this is SEBI-mandated clearing, not a scam.'"
    }
]


# ----------------------------------------------------------------------
# Benchmark Evaluator
# ----------------------------------------------------------------------
def evaluate_golden_set(
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Runs the 20 Golden Set benchmark cases through the analyzer pipeline
    and compares AI predictions against Human Ground Truth.
    """
    results = []
    milestone_matches = 0
    category_matches = 0
    severity_matches = 0
    full_matches = 0

    for item in GOLDEN_SET_ITEMS:
        raw_text = item["raw_text"]
        gt = item["human_ground_truth"]

        pred = analyze_review(raw_text, api_key=api_key, model_name=model_name)

        m_match = (pred.get("milestone") == gt["milestone"])
        c_match = (pred.get("friction_category") == gt["friction_category"])
        s_match = (pred.get("severity") == gt["severity"])
        full_match = (m_match and c_match and s_match)

        if m_match: milestone_matches += 1
        if c_match: category_matches += 1
        if s_match: severity_matches += 1
        if full_match: full_matches += 1

        results.append({
            "id": item["id"],
            "raw_text": raw_text,
            "source": item["source"],
            "context_tags": item["context_tags"],
            "ground_truth": gt,
            "ai_prediction": pred,
            "agreement": {
                "milestone_match": m_match,
                "category_match": c_match,
                "severity_match": s_match,
                "overall_match": full_match
            }
        })

    total = len(GOLDEN_SET_ITEMS)
    stats = {
        "total_items": total,
        "overall_agreement_rate": round((full_matches / total) * 100, 1),
        "milestone_agreement_rate": round((milestone_matches / total) * 100, 1),
        "category_agreement_rate": round((category_matches / total) * 100, 1),
        "severity_agreement_rate": round((severity_matches / total) * 100, 1),
        "full_matches_count": full_matches,
        "disagreements_count": total - full_matches
    }

    output_data = {
        "metadata": {
            "name": "Groww SIP Discovery Engine - Curated 20-Item Golden Benchmark",
            "version": "1.0.0",
            "target_problem": "12-Month SIP Retention for First-Time Mutual Fund Investors",
            "evaluator_engine": results[0]["ai_prediction"].get("engine_used", "Unknown") if results else "None"
        },
        "stats": stats,
        "documented_corrections": DOCUMENTED_CORRECTION_CASES,
        "benchmark_items": results
    }

    return output_data


def generate_and_save_golden_set(
    output_path: str = "data/golden_set.json",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Generates benchmark data and persists to disk."""
    data = evaluate_golden_set(api_key=api_key)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Golden Set generated & saved to '{output_path}'. Overall Agreement: {data['stats']['overall_agreement_rate']}%")
    return data


def load_golden_set(json_path: str = "data/golden_set.json") -> Dict[str, Any]:
    """Loads existing Golden Set from disk or generates fresh one."""
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading {json_path}: {e}. Regenerating...")
    return generate_and_save_golden_set(output_path=json_path)


if __name__ == "__main__":
    benchmark = generate_and_save_golden_set()
    stats = benchmark["stats"]
    print("\n--- GOLDEN SET BENCHMARK PERFORMANCE ---")
    print(f"Total Benchmark Cases: {stats['total_items']}")
    print(f"Overall Agreement Rate: {stats['overall_agreement_rate']}%")
    print(f"Milestone Agreement Rate: {stats['milestone_agreement_rate']}%")
    print(f"Friction Category Agreement Rate: {stats['category_agreement_rate']}%")
    print(f"Severity Agreement Rate: {stats['severity_agreement_rate']}%")
    print(f"Documented Rejection/Correction Cases: {len(benchmark['documented_corrections'])}")
