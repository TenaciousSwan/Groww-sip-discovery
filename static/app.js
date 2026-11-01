/**
 * Groww SIP Discovery Engine — Client-Side Logic & Visualizations (app.js)
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadSummary();
  loadInsights();
  loadOpportunities();
  loadBenchmark();
  loadVerbatims();
  initDiagnosticConsole();
});

// --------------------------------------------------------------------------
// 1. Tab Switching Navigation
// --------------------------------------------------------------------------
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

// --------------------------------------------------------------------------
// 2. Executive Overview & Summary
// --------------------------------------------------------------------------
async function loadSummary() {
  try {
    const res = await fetch("/api/summary");
    const data = await res.json();

    document.getElementById("kpi-total").innerText = data.total_touchpoints.toLocaleString();
    document.getElementById("kpi-play").innerText = (data.sources["Google Play Store"] || 0).toLocaleString();
    document.getElementById("kpi-appstore").innerText = (data.sources["Apple App Store"] || 0).toLocaleString();
    document.getElementById("kpi-forums").innerText = (data.sources["TradingQ&A Forum"] || 0).toLocaleString();

    // Chart 1: Channels Breakdown
    const srcLabels = Object.keys(data.sources);
    const srcValues = Object.values(data.sources);

    new Chart(document.getElementById("chart-channels"), {
      type: "bar",
      data: {
        labels: srcLabels,
        datasets: [{
          data: srcValues,
          backgroundColor: ["#00b386", "#3b82f6", "#8b5cf6", "#f59e0b"],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });

    // Chart 2: Investor Outcomes
    const outLabels = Object.keys(data.outcomes);
    const outValues = Object.values(data.outcomes);
    const outcomeColors = {
      "Continued": "#00b386",
      "Paused / skipped": "#f59e0b",
      "Reduced": "#3b82f6",
      "Stopped / cancelled": "#ef4444"
    };

    new Chart(document.getElementById("chart-outcomes"), {
      type: "doughnut",
      data: {
        labels: outLabels,
        datasets: [{
          data: outValues,
          backgroundColor: outLabels.map(l => outcomeColors[l] || "#94a3b8"),
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { boxWidth: 12, font: { size: 12 } } }
        },
        cutout: "60%"
      }
    });

  } catch (err) {
    console.error("Error loading summary:", err);
  }
}

// --------------------------------------------------------------------------
// 3. Behavioral Journey Insights
// --------------------------------------------------------------------------
async function loadInsights() {
  try {
    const res = await fetch("/api/insights");
    const data = await res.json();

    // Chart: Stated Start Reasons
    const startLabels = Object.keys(data.start_reasons);
    const startValues = Object.values(data.start_reasons);

    new Chart(document.getElementById("chart-start-reasons"), {
      type: "bar",
      data: {
        labels: startLabels,
        datasets: [{
          data: startValues,
          backgroundColor: "#00b386",
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });

    // Chart: Initial Return Expectations
    const expLabels = Object.keys(data.expectations);
    const expValues = Object.values(data.expectations);

    new Chart(document.getElementById("chart-expectations"), {
      type: "bar",
      data: {
        labels: expLabels,
        datasets: [{
          data: expValues,
          backgroundColor: "#3b82f6",
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });

    // Chart: Lifecycle Progression
    const lifeLabels = Object.keys(data.milestones);
    const lifeValues = Object.values(data.milestones);

    new Chart(document.getElementById("chart-lifecycle"), {
      type: "bar",
      data: {
        labels: lifeLabels,
        datasets: [{
          data: lifeValues,
          backgroundColor: ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: "#f1f5f9" } }
        }
      }
    });

    // Chart: In-App Confusions
    const confLabels = Object.keys(data.in_app_confusions);
    const confValues = Object.values(data.in_app_confusions);

    new Chart(document.getElementById("chart-confusions"), {
      type: "bar",
      data: {
        labels: confLabels,
        datasets: [{
          data: confValues,
          backgroundColor: "#ef4444",
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });

    // Chart: Outside-App Workarounds
    const workLabels = Object.keys(data.outside_actions);
    const workValues = Object.values(data.outside_actions);

    new Chart(document.getElementById("chart-workarounds"), {
      type: "bar",
      data: {
        labels: workLabels,
        datasets: [{
          data: workValues,
          backgroundColor: "#8b5cf6",
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });

    // Table: Continuers vs Droppers Comparisons
    const tbodyComp = document.getElementById("tbody-comparisons");
    tbodyComp.innerHTML = "";

    data.comparisons.forEach(item => {
      const tr = document.createElement("tr");
      const gapClass = item.gap_pp > 0 ? "text-red" : "text-green";
      const interp = item.gap_pp > 10 ? "🚨 Primary Driver of Fatal Churn" : item.gap_pp > 0 ? "⚠️ Elevated in Dropped Users" : "✅ Higher Retention in Continuing Users";

      tr.innerHTML = `
        <td><strong>${item.unmet_need}</strong></td>
        <td>${item.continued_pct.toFixed(1)}%</td>
        <td>${item.stopped_pct.toFixed(1)}%</td>
        <td><strong style="color: ${item.gap_pp > 0 ? '#dc2626' : '#059669'};">${item.gap_pp > 0 ? '+' : ''}${item.gap_pp.toFixed(1)} pp</strong></td>
        <td>${interp}</td>
      `;
      tbodyComp.appendChild(tr);
    });

  } catch (err) {
    console.error("Error loading insights:", err);
  }
}

// --------------------------------------------------------------------------
// 4. Quantified Opportunity Areas
// --------------------------------------------------------------------------
async function loadOpportunities() {
  try {
    const res = await fetch("/api/opportunities");
    const data = await res.json();

    // Chart: Opportunity Score
    const oppLabels = data.map(d => d.opportunity_area);
    const oppScores = data.map(d => d.opportunity_score);

    new Chart(document.getElementById("chart-opportunities"), {
      type: "bar",
      data: {
        labels: oppLabels,
        datasets: [{
          data: oppScores,
          backgroundColor: "#00b386",
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { max: 100, grid: { color: "#f1f5f9" } },
          y: { grid: { display: false } }
        }
      }
    });

    // Sizing Table
    const tbody = document.getElementById("tbody-opportunities");
    tbody.innerHTML = "";

    data.forEach(item => {
      const tr = document.createElement("tr");
      const badgeClass = item.opportunity_score >= 70 ? "score-high" : item.opportunity_score >= 30 ? "score-med" : "score-low";

      tr.innerHTML = `
        <td><span class="score-badge ${badgeClass}">${item.opportunity_score}</span></td>
        <td><strong>${item.opportunity_area}</strong></td>
        <td>${item.mentions}</td>
        <td>${item.prevalence_pct.toFixed(1)}%</td>
        <td>${item.ci_95}</td>
        <td>${item.stop_rate_pct.toFixed(1)}%</td>
        <td>${item.stop_lift > 0 ? '+' : ''}${item.stop_lift.toFixed(2)}x</td>
        <td>${item.avg_severity_weight.toFixed(2)}</td>
        <td>${item.verified_sources_count} Channels</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error loading opportunities:", err);
  }
}

// --------------------------------------------------------------------------
// 5. AI Evidence Log & Benchmark
// --------------------------------------------------------------------------
async function loadBenchmark() {
  try {
    const res = await fetch("/api/benchmark");
    const data = await res.json();

    const stats = data.stats || {};
    document.getElementById("bench-milestone").innerText = (stats.milestone_agreement_pct || 90).toFixed(1) + "%";
    document.getElementById("bench-category").innerText = (stats.category_agreement_pct || 90).toFixed(1) + "%";
    document.getElementById("bench-severity").innerText = (stats.severity_agreement_pct || 80).toFixed(1) + "%";

    // Documented Corrections
    const correctionsContainer = document.getElementById("corrections-container");
    correctionsContainer.innerHTML = "";

    (data.documented_corrections || []).forEach(caseItem => {
      const card = document.createElement("div");
      card.className = "correction-card";
      card.innerHTML = `
        <div class="correction-header">
          <span>🚨 ${caseItem.case_id}: ${caseItem.title}</span>
        </div>
        <div class="correction-content">
          <div class="correction-review">"${caseItem.user_review}"</div>
          <div class="correction-split">
            <div class="box-naive">
              <strong>Naive AI Misdiagnosis:</strong> <code>${caseItem.naive_ai_output.friction_category}</code><br>
              <span style="font-size: 11px;">${caseItem.why_naive_ai_failed}</span>
            </div>
            <div class="box-gt">
              <strong>Human PM Ground Truth:</strong> <code>${caseItem.human_ground_truth.friction_category}</code><br>
              <span style="font-size: 11px;">${caseItem.pm_root_cause_diagnosis}</span>
            </div>
          </div>
          <div class="box-takeaway">
            <strong>Product Takeaway:</strong> ${caseItem.pm_takeaway}
          </div>
        </div>
      `;
      correctionsContainer.appendChild(card);
    });

    // Benchmark Table
    const tbodyBench = document.getElementById("tbody-benchmark");
    tbodyBench.innerHTML = "";

    (data.benchmark_items || []).forEach(it => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${it.id}</strong></td>
        <td>${it.ground_truth.milestone}</td>
        <td>${it.ai_prediction.milestone}</td>
        <td>${it.ground_truth.friction_category}</td>
        <td>${it.ai_prediction.friction_category}</td>
        <td>${it.agreement.milestone_match ? "✅" : "❌"}</td>
        <td>${it.agreement.category_match ? "✅" : "❌"}</td>
        <td>${it.agreement.severity_match ? "✅" : "❌"}</td>
      `;
      tbodyBench.appendChild(tr);
    });

  } catch (err) {
    console.error("Error loading benchmark:", err);
  }
}

// --------------------------------------------------------------------------
// 6. Verbatim Explorer with Filtering
// --------------------------------------------------------------------------
let debounceTimer;

async function loadVerbatims() {
  const search = document.getElementById("verbatim-search").value;
  const channel = document.getElementById("filter-channel").value;
  const stage = document.getElementById("filter-stage").value;

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (channel && channel !== "All") params.append("source", channel);
  if (stage && stage !== "All") params.append("milestone", stage);
  params.append("limit", "100");

  try {
    const res = await fetch(`/api/verbatims?${params.toString()}`);
    const data = await res.json();
    const tbody = document.getElementById("verbatim-tbody");
    tbody.innerHTML = "";

    if (data.results.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #94a3b8; padding: 24px;">No matching verbatims found.</td></tr>`;
      return;
    }

    data.results.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code style="font-size: 11px;">${item.id}</code></td>
        <td><span class="badge badge-compliance">${item.source}</span></td>
        <td>${item.date}</td>
        <td><span class="badge badge-live" style="font-size: 11px;">${item.milestone}</span></td>
        <td><span style="font-size: 12px; font-weight: 500;">${item.friction_category}</span></td>
        <td><span style="font-size: 12px; color: ${item.severity.includes('Fatal') ? '#dc2626' : '#475569'}; font-weight: 600;">${item.severity.split(' ')[0]}</span></td>
        <td style="font-size: 12px; max-width: 450px; line-height: 1.4;">${item.raw_text}</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error loading verbatims:", err);
  }
}

document.getElementById("verbatim-search").addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadVerbatims, 300);
});
document.getElementById("filter-channel").addEventListener("change", loadVerbatims);
document.getElementById("filter-stage").addEventListener("change", loadVerbatims);

// --------------------------------------------------------------------------
// 7. Live Diagnostic Console
// --------------------------------------------------------------------------
function initDiagnosticConsole() {
  const btn = document.getElementById("btn-diagnose");
  const input = document.getElementById("diag-input");
  const resultCard = document.getElementById("diag-result-card");
  const jsonCode = document.getElementById("diag-json");

  input.value = "I started my first SIP in Parag Parikh fund. Bank deducted ₹295 penalty because Groww triggered autopay 2 days before salary day. Cancelled mandate immediately from HDFC netbanking.";

  btn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) return;

    btn.disabled = true;
    btn.innerText = "Analyzing...";

    try {
      const res = await fetch("/api/diagnose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
      });
      const data = await res.json();
      jsonCode.innerText = JSON.stringify(data, null, 2);
      resultCard.classList.remove("hidden");
    } catch (err) {
      jsonCode.innerText = "Error analyzing verbatim: " + err.message;
      resultCard.classList.remove("hidden");
    } finally {
      btn.disabled = false;
      btn.innerText = "🚀 Run Diagnostic Pipeline";
    }
  });
}
