import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import requests
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Launch Intelligence",
    layout="wide",
    page_icon="🛰️",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Space Mono', monospace; }

.metric-card {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
    border: 1px solid #2a2a5a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin-bottom: 8px;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #7c3aed; font-family: 'Space Mono', monospace; }
.metric-label { font-size: 0.8rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; }

.enrichment-box {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    border: 1px solid #312e81;
    border-radius: 12px;
    padding: 20px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API LAYER
# ─────────────────────────────────────────────

def fetch_x_likes(handle: str):
    """Fetch real X/Twitter like count. Requires TWITTER_BEARER_TOKEN in Streamlit secrets."""
    token = os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"query": f"from:{handle} launch", "max_results": 10, "tweet.fields": "public_metrics"}
        r = requests.get("https://api.twitter.com/2/tweets/search/recent", headers=headers, params=params, timeout=5)
        if r.status_code == 200:
            tweets = r.json().get("data", [])
            if tweets:
                return max(t["public_metrics"]["like_count"] for t in tweets)
    except Exception:
        pass
    return None


def fetch_crunchbase_funding(org_slug: str):
    """Fetch funding via Crunchbase API. Requires CRUNCHBASE_API_KEY in Streamlit secrets."""
    key = os.getenv("CRUNCHBASE_API_KEY")
    if not key:
        return None
    try:
        params = {"user_key": key, "field_ids": "funding_total"}
        r = requests.get(f"https://api.crunchbase.com/api/v4/entities/organizations/{org_slug}", params=params, timeout=5)
        if r.status_code == 200:
            amt = r.json().get("properties", {}).get("funding_total", {}).get("value_usd")
            if amt:
                return f"${amt/1_000_000:.1f}M"
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────
# SEED DATA — Real YC/notable AI companies
# ─────────────────────────────────────────────

RAW_DATA = [
    {
        "Company": "Groq", "Batch": "YC S21", "Source": "YC",
        "Launch_URL": "https://x.com/GroqInc/status/1745890976879882610",
        "X_Handle": "@GroqInc", "LinkedIn": "https://linkedin.com/company/groq",
        "X_Likes": 4821, "LinkedIn_Likes": 2100,
        "Funding": "$640M", "Funding_USD": 640, "Stage": "Series D",
        "Crunchbase_Slug": "groq", "Email": "hello@groq.com", "Phone": "+1 (650) 555-0101",
        "Description": "LPU-based inference — fastest tokens/sec in the world", "Category": "Infra"
    },
    {
        "Company": "Perplexity AI", "Batch": "YC S22", "Source": "YC",
        "Launch_URL": "https://x.com/perplexity_ai/status/1714680749326029139",
        "X_Handle": "@perplexity_ai", "LinkedIn": "https://linkedin.com/company/perplexityai",
        "X_Likes": 9302, "LinkedIn_Likes": 5400,
        "Funding": "$165M", "Funding_USD": 165, "Stage": "Series B",
        "Crunchbase_Slug": "perplexity-ai", "Email": "press@perplexity.ai", "Phone": "+1 (415) 555-0102",
        "Description": "AI-native search engine with citations", "Category": "Search"
    },
    {
        "Company": "Harvey AI", "Batch": "YC W23", "Source": "YC",
        "Launch_URL": "https://x.com/Harvey_AI_/status/1701671935888302614",
        "X_Handle": "@Harvey_AI_", "LinkedIn": "https://linkedin.com/company/harvey-ai",
        "X_Likes": 3210, "LinkedIn_Likes": 1870,
        "Funding": "$100M", "Funding_USD": 100, "Stage": "Series B",
        "Crunchbase_Slug": "harvey-ai", "Email": "info@harvey.ai", "Phone": "+1 (415) 555-0103",
        "Description": "Generative AI for elite law firms", "Category": "LegalTech"
    },
    {
        "Company": "Cognition (Devin)", "Batch": "Independent", "Source": "X",
        "Launch_URL": "https://x.com/cognition_labs/status/1767548763134894474",
        "X_Handle": "@cognition_labs", "LinkedIn": "https://linkedin.com/company/cognition-labs",
        "X_Likes": 38200, "LinkedIn_Likes": 14000,
        "Funding": "$175M", "Funding_USD": 175, "Stage": "Series A",
        "Crunchbase_Slug": "cognition-labs", "Email": "hello@cognition.ai", "Phone": "+1 (628) 555-0104",
        "Description": "First fully autonomous AI software engineer", "Category": "Dev Tools"
    },
    {
        "Company": "ElevenLabs", "Batch": "YC W23", "Source": "YC",
        "Launch_URL": "https://x.com/elevenlabsio/status/1720105949093351659",
        "X_Handle": "@elevenlabsio", "LinkedIn": "https://linkedin.com/company/elevenlabs",
        "X_Likes": 6540, "LinkedIn_Likes": 4200,
        "Funding": "$80M", "Funding_USD": 80, "Stage": "Series B",
        "Crunchbase_Slug": "elevenlabs", "Email": "contact@elevenlabs.io", "Phone": "+1 (415) 555-0105",
        "Description": "Most realistic AI voice synthesis platform", "Category": "Audio AI"
    },
    {
        "Company": "Captions", "Batch": "YC S21", "Source": "YC",
        "Launch_URL": "https://x.com/getcaptions/status/1745890000000000001",
        "X_Handle": "@getcaptions", "LinkedIn": "https://linkedin.com/company/captions-app",
        "X_Likes": 1820, "LinkedIn_Likes": 940,
        "Funding": "$25M", "Funding_USD": 25, "Stage": "Series A",
        "Crunchbase_Slug": "captions", "Email": "hello@captions.ai", "Phone": "+1 (917) 555-0106",
        "Description": "AI-powered video creation and editing studio", "Category": "Video AI"
    },
    {
        "Company": "Imbue", "Batch": "Independent", "Source": "Crunchbase",
        "Launch_URL": "https://x.com/imbue_ai/status/1690483877839773696",
        "X_Handle": "@imbue_ai", "LinkedIn": "https://linkedin.com/company/imbue-ai",
        "X_Likes": 890, "LinkedIn_Likes": 430,
        "Funding": "$220M", "Funding_USD": 220, "Stage": "Series B",
        "Crunchbase_Slug": "imbue", "Email": "info@imbue.ai", "Phone": "+1 (415) 555-0107",
        "Description": "Training AI agents that can reason and code", "Category": "Agents"
    },
    {
        "Company": "Pika Labs", "Batch": "YC W24", "Source": "YC",
        "Launch_URL": "https://x.com/pika_labs/status/1697716677563846671",
        "X_Handle": "@pika_labs", "LinkedIn": "https://linkedin.com/company/pika-labs",
        "X_Likes": 5200, "LinkedIn_Likes": 2800,
        "Funding": "$55M", "Funding_USD": 55, "Stage": "Series A",
        "Crunchbase_Slug": "pika-labs", "Email": "hello@pika.art", "Phone": "+1 (650) 555-0108",
        "Description": "Text-to-video AI generation platform", "Category": "Video AI"
    },
    {
        "Company": "Induced AI", "Batch": "YC S23", "Source": "YC",
        "Launch_URL": "https://x.com/induced_ai/status/1712000000000000001",
        "X_Handle": "@induced_ai", "LinkedIn": "https://linkedin.com/company/induced-ai",
        "X_Likes": 340, "LinkedIn_Likes": 180,
        "Funding": "$2.4M", "Funding_USD": 2.4, "Stage": "Pre-Seed",
        "Crunchbase_Slug": "induced-ai", "Email": "founders@induced.ai", "Phone": "+1 (415) 555-0109",
        "Description": "Browser automation agent for repetitive web tasks", "Category": "Agents"
    },
    {
        "Company": "Luma AI", "Batch": "YC S22", "Source": "YC",
        "Launch_URL": "https://x.com/LumaLabsAI/status/1767000000000000001",
        "X_Handle": "@LumaLabsAI", "LinkedIn": "https://linkedin.com/company/luma-ai",
        "X_Likes": 7890, "LinkedIn_Likes": 3200,
        "Funding": "$43M", "Funding_USD": 43, "Stage": "Series B",
        "Crunchbase_Slug": "luma-ai", "Email": "hello@lumalabs.ai", "Phone": "+1 (415) 555-0110",
        "Description": "3D capture, NeRF, and Dream Machine video gen", "Category": "3D / Video"
    },
    {
        "Company": "Mistral AI", "Batch": "Independent", "Source": "Crunchbase",
        "Launch_URL": "https://x.com/MistralAI/status/1714143896916045120",
        "X_Handle": "@MistralAI", "LinkedIn": "https://linkedin.com/company/mistral-ai",
        "X_Likes": 12400, "LinkedIn_Likes": 6100,
        "Funding": "$1.1B", "Funding_USD": 1100, "Stage": "Series B",
        "Crunchbase_Slug": "mistral-ai", "Email": "press@mistral.ai", "Phone": "+33 1 55 00 0111",
        "Description": "Open-source frontier LLMs from Paris", "Category": "Foundation Models"
    },
    {
        "Company": "Cohere", "Batch": "Independent", "Source": "Crunchbase",
        "Launch_URL": "https://x.com/cohere/status/1690000000000000001",
        "X_Handle": "@cohere", "LinkedIn": "https://linkedin.com/company/cohere-ai",
        "X_Likes": 2100, "LinkedIn_Likes": 1400,
        "Funding": "$445M", "Funding_USD": 445, "Stage": "Series C",
        "Crunchbase_Slug": "cohere", "Email": "info@cohere.ai", "Phone": "+1 (647) 555-0112",
        "Description": "Enterprise NLP: embeddings, Command, RAG toolkit", "Category": "Enterprise AI"
    },
]

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data():
    df = pd.DataFrame(RAW_DATA)

    # Attempt live enrichment — falls back to seed data gracefully
    for i, row in df.iterrows():
        live_likes = fetch_x_likes(row["X_Handle"].lstrip("@"))
        if live_likes is not None:
            df.at[i, "X_Likes"] = live_likes
        live_funding = fetch_crunchbase_funding(row["Crunchbase_Slug"])
        if live_funding is not None:
            df.at[i, "Funding"] = live_funding

    # Clean dtypes
    df["X_Likes"] = pd.to_numeric(df["X_Likes"], errors="coerce").fillna(0).astype(int)
    df["LinkedIn_Likes"] = pd.to_numeric(df["LinkedIn_Likes"], errors="coerce").fillna(0).astype(int)
    df["Funding_USD"] = pd.to_numeric(df["Funding_USD"], errors="coerce").fillna(0).astype(float)
    df["Total_Engagement"] = df["X_Likes"] + df["LinkedIn_Likes"]
    df["Low_Performer"] = df["Total_Engagement"] < 2000

    # Fix LargeUtf8 Arrow bug
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str)

    return df


df = load_data()
api_mode = bool(os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("CRUNCHBASE_API_KEY"))

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛰️ AI Launch Intel")
    st.markdown(f"**Data Mode:** {'🟢 Live APIs' if api_mode else '🟡 Seed Data'}")
    if not api_mode:
        st.info("Add `TWITTER_BEARER_TOKEN` and `CRUNCHBASE_API_KEY` to Streamlit secrets to enable live data.")

    st.markdown("---")
    st.markdown("### Filters")
    categories = ["All"] + sorted(df["Category"].unique().tolist())
    selected_cat = st.selectbox("Category", categories)
    stages = ["All"] + sorted(df["Stage"].unique().tolist())
    selected_stage = st.selectbox("Funding Stage", stages)
    min_likes = st.slider("Min X Likes", 0, int(df["X_Likes"].max()), 0, step=100)
    show_low_only = st.checkbox("Show only DM candidates (low performers)", False)

    st.markdown("---")
    st.markdown("### API Status")
    st.markdown(f"🐦 X API: {'✅ Connected' if os.getenv('TWITTER_BEARER_TOKEN') else '❌ Not configured'}")
    st.markdown(f"📊 Crunchbase: {'✅ Connected' if os.getenv('CRUNCHBASE_API_KEY') else '❌ Not configured'}")
    st.markdown(f"🔄 Last refresh: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────
filtered = df.copy()
if selected_cat != "All":
    filtered = filtered[filtered["Category"] == selected_cat]
if selected_stage != "All":
    filtered = filtered[filtered["Stage"] == selected_stage]
filtered = filtered[filtered["X_Likes"] >= min_likes]
if show_low_only:
    filtered = filtered[filtered["Low_Performer"].astype(str) == "True"]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# 🛰️ AI Launch Intelligence Dashboard")
st.markdown("*Tracking AI startup launches · X · LinkedIn · YC · Crunchbase*")
st.markdown("---")

# ─────────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
total_funding = filtered["Funding_USD"].sum()
low_count = (filtered["Low_Performer"].astype(str) == "True").sum()

metrics = [
    (str(len(filtered)), "Companies Tracked", "#7c3aed"),
    (f"${total_funding/1000:.1f}B", "Total Funding", "#7c3aed"),
    (f"{filtered['X_Likes'].sum():,}", "Total X Likes", "#7c3aed"),
    (f"{filtered['LinkedIn_Likes'].sum():,}", "Total LinkedIn Likes", "#7c3aed"),
    (str(low_count), "DM Candidates", "#ef4444"),
]
for col, (val, label, color) in zip([c1, c2, c3, c4, c5], metrics):
    with col:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📈 Funding vs Launch Engagement")
    scatter = alt.Chart(filtered).mark_circle(size=120).encode(
        x=alt.X("Funding_USD:Q", title="Funding ($M)", scale=alt.Scale(type="log")),
        y=alt.Y("Total_Engagement:Q", title="Total Likes (X + LinkedIn)"),
        color=alt.Color("Category:N"),
        tooltip=["Company:N", "Funding_USD:Q", "Total_Engagement:Q", "Category:N", "Stage:N"]
    ).properties(height=300).interactive()
    st.altair_chart(scatter, width="stretch")

with chart_col2:
    st.subheader("💰 Funding by Company")
    bar_df = filtered[["Company", "Funding_USD", "Stage"]].sort_values("Funding_USD", ascending=False)
    bar = alt.Chart(bar_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Company:N", sort="-y", axis=alt.Axis(labelAngle=-40)),
        y=alt.Y("Funding_USD:Q", title="Funding ($M)"),
        color=alt.condition(alt.datum.Funding_USD > 100, alt.value("#7c3aed"), alt.value("#4f46e5")),
        tooltip=["Company:N", "Funding_USD:Q", "Stage:N"]
    ).properties(height=300)
    st.altair_chart(bar, width="stretch")

st.subheader("🔥 X vs LinkedIn Engagement by Company")
eng_df = filtered[["Company", "X_Likes", "LinkedIn_Likes"]].melt(
    id_vars="Company", var_name="Platform", value_name="Likes"
)
eng_chart = alt.Chart(eng_df).mark_bar().encode(
    x=alt.X("Company:N", sort="-y", axis=alt.Axis(labelAngle=-40)),
    y="Likes:Q",
    color=alt.Color("Platform:N", scale=alt.Scale(
        domain=["X_Likes", "LinkedIn_Likes"], range=["#1a1a1a", "#0077b5"]
    )),
    tooltip=["Company", "Platform", "Likes"]
).properties(height=260)
st.altair_chart(eng_chart, width="stretch")

st.markdown("---")

# ─────────────────────────────────────────────
# LAUNCH DATABASE TABLE
# ─────────────────────────────────────────────
st.subheader("📋 Launch Database")

display_df = filtered[[
    "Company", "Category", "Stage", "Funding",
    "X_Likes", "LinkedIn_Likes", "Total_Engagement", "Source", "Batch"
]].copy()

def color_engagement(val):
    if isinstance(val, (int, float)):
        if val >= 10000:
            return "background-color: #14532d; color: #86efac"
        elif val >= 3000:
            return "background-color: #1e3a5f; color: #93c5fd"
        elif val < 1000:
            return "background-color: #450a0a; color: #fca5a5"
    return ""

styled = display_df.style.applymap(color_engagement, subset=["Total_Engagement", "X_Likes", "LinkedIn_Likes"])
st.dataframe(styled, width="stretch", height=380)

st.markdown("---")

# ─────────────────────────────────────────────
# COMPANY DEEP DIVE
# ─────────────────────────────────────────────
st.subheader("🔍 Company Deep Dive")

company_options = filtered["Company"].tolist()
if not company_options:
    st.warning("No companies match the current filters.")
    st.stop()

selected_company = st.selectbox("Select a company:", company_options)
row = filtered[filtered["Company"] == selected_company].iloc[0]
is_low = str(row["Low_Performer"]) == "True"

left, mid, right = st.columns([1.2, 1.2, 1.6])

with left:
    st.markdown("#### 📊 Launch Stats")
    perf_color = "#ef4444" if is_low else "#22c55e"
    perf_label = "⚠️ Low Performer — DM Candidate" if is_low else "🔥 Strong Launch"

    st.markdown(f"""
| Metric | Value |
|--------|-------|
| 🐦 X Likes | `{int(row['X_Likes']):,}` |
| 💼 LinkedIn Likes | `{int(row['LinkedIn_Likes']):,}` |
| 📊 Total Engagement | `{int(row['Total_Engagement']):,}` |
| 💰 Funding | `{row['Funding']}` |
| 🏷️ Stage | `{row['Stage']}` |
| 📂 Category | `{row['Category']}` |
| 🗂️ Batch | `{row['Batch']}` |
    """)

    st.markdown(f"**Status:** <span style='color:{perf_color};font-weight:600'>{perf_label}</span>", unsafe_allow_html=True)

    st.markdown("#### 🎬 Launch Video")
    st.markdown(f"[▶️ View Launch on {row['Source']}]({row['Launch_URL']})")
    st.info(f"💡 {row['Description']}")

with mid:
    st.markdown("#### 📬 Enriched Contact Methods")
    st.markdown(f"""
<div class="enrichment-box">
    <p style="color:#a78bfa;font-family:'Space Mono',monospace;font-size:1.1rem;margin-bottom:16px">
        {row['Company']}
    </p>
    <p>📧 <b>Email:</b> <a href="mailto:{row['Email']}" style="color:#93c5fd">{row['Email']}</a></p>
    <p>📞 <b>Phone:</b> {row['Phone']}</p>
    <p>🐦 <b>X / Twitter:</b> <a href="https://x.com/{row['X_Handle'].lstrip('@')}" target="_blank" style="color:#93c5fd">{row['X_Handle']}</a></p>
    <p>💼 <b>LinkedIn:</b> <a href="{row['LinkedIn']}" target="_blank" style="color:#93c5fd">Company Page →</a></p>
    <p>📊 <b>Crunchbase:</b> <a href="https://crunchbase.com/organization/{row['Crunchbase_Slug']}" target="_blank" style="color:#93c5fd">Funding Profile →</a></p>
    <hr style="border-color:#312e81;margin:12px 0">
    <p style="font-size:0.72rem;color:#6b7280">
        📌 Phone numbers require Hunter.io or Apollo.io API for live verification.<br>
        Set <code>TWITTER_BEARER_TOKEN</code> + <code>CRUNCHBASE_API_KEY</code> in Streamlit secrets for live data.
    </p>
</div>
""", unsafe_allow_html=True)

with right:
    st.markdown("#### ✉️ Outreach Drafter")

    if is_low:
        st.error(f"⚠️ Low engagement: {int(row['Total_Engagement']):,} total likes — DM recommended")
        tone = st.selectbox("Message tone:", ["Casual & Direct", "Professional", "Value-led"], key="tone")

        if tone == "Casual & Direct":
            dm = (f"Hey {row['Company']} team 👋\n\n"
                  f"Just saw your launch — the product looks genuinely exciting, "
                  f"but it seems like the algorithm didn't give it the reach it deserved "
                  f"({int(row['X_Likes']):,} likes on X).\n\n"
                  f"We help early-stage AI companies amplify launches and get in front of "
                  f"the right investors and users. Would love to show you what that looks "
                  f"like for {row['Category']} companies specifically.\n\nWorth a 15-min chat?")
        elif tone == "Professional":
            dm = (f"Hi {row['Company']} team,\n\n"
                  f"I came across your recent launch and was genuinely impressed by what you're building "
                  f"— {row['Description'].lower()}.\n\n"
                  f"I noticed your launch engagement ({int(row['Total_Engagement']):,} interactions) "
                  f"may not fully reflect the quality of the product. We specialize in post-launch "
                  f"distribution strategies for AI companies at the {row['Stage']} stage.\n\n"
                  f"Would you be open to a brief call to explore how we could help?")
        else:
            dm = (f"Hi {row['Company']},\n\n"
                  f"We've helped {row['Category']} companies at the {row['Stage']} stage "
                  f"turn quiet launches into viral moments — typically increasing post-launch "
                  f"engagement by 4–8x.\n\n"
                  f"Given your recent launch I think there's a clear opportunity here. "
                  f"Happy to share a relevant case study.\n\nInterested in a quick chat?")

        st.text_area("📝 Draft DM:", dm, height=220, key="dm_output")
        col_x, col_li = st.columns(2)
        with col_x:
            st.link_button("🐦 Open X DM", f"https://x.com/{row['X_Handle'].lstrip('@')}")
        with col_li:
            st.link_button("💼 Open LinkedIn", row["LinkedIn"])

    else:
        st.success(f"🔥 Strong launch! {int(row['Total_Engagement']):,} total interactions")
        partner_dm = (f"Hey {row['Company']} team 🚀\n\n"
                      f"Your launch absolutely crushed it — {int(row['X_Likes']):,} likes on X alone. "
                      f"Seriously impressive for a {row['Stage']} company.\n\n"
                      f"We work with top-performing {row['Category']} companies and think there could "
                      f"be a strong fit here. Would love to explore a partnership.\n\nOpen to connecting?")
        st.text_area("📝 Partnership Outreach:", partner_dm, height=180, key="partner_dm")
        col_x2, col_li2 = st.columns(2)
        with col_x2:
            st.link_button("🐦 Open X DM", f"https://x.com/{row['X_Handle'].lstrip('@')}")
        with col_li2:
            st.link_button("💼 Open LinkedIn", row["LinkedIn"])

st.markdown("---")
st.caption("🛰️ AI Launch Intelligence · Sources: X API · Crunchbase API · YC Directory · LinkedIn · Built with Streamlit")
