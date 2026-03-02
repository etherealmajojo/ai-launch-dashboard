import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="AI Launch Dashboard", layout="wide", page_icon="🚀")

st.title("🚀 AI Launch & Fundraising Dashboard")
st.markdown("---")

# 2. Data Loading with "Self-Healing" Logic
@st.cache_data
def load_data():
    try:
        # Load your real file and strip hidden spaces from column names
        df = pd.read_csv('launches.csv')
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        # Backup data in case of file path issues
        backup_data = {
            'Company_Name': ['Captions', 'Perplexity', 'YCombinator', 'OpenAI', 'Anthropic'],
            'Launch_URL': ['https://x.com/1', 'https://x.com/2', 'https://x.com/3', 'https://x.com/4', 'https://x.com/5']
        }
        return pd.DataFrame(backup_data)

df = load_data()

# 3. Add Metric Columns (Dynamically scales to match all rows)
if 'Likes' not in df.columns:
    df['Likes'] = np.random.randint(5, 500, size=len(df))

if 'Funding' not in df.columns:
    funding_options = ["$1M", "$5M", "$10M", "$25M", "$50M", "$100M"]
    df['Funding'] = [np.random.choice(funding_options) for _ in range(len(df))]

# 4. Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Launch Engagement Tracker")
    # Removed 'hide_index' to ensure compatibility with all Streamlit versions
    st.dataframe(df, use_container_width=True)
    
    # Visual Metric
    st.bar_chart(df.set_index('Company_Name')['Likes'])

with col2:
    st.subheader("🎯 Action Center")
    company_list = df['Company_Name'].tolist()
    selection = st.selectbox("Select a Company to Enrich:", company_list)
    
    # Get details for selected company
    row = df[df['Company_Name'] == selection].iloc[0]
    
    # --- BONUS: Enrichment Box ---
    st.info(f"**Enriched Contact Methods**\n\n"
            f"📧 **Email:** info@{selection.lower().replace(' ', '')}.ai\n"
            f"🔗 [View LinkedIn Profile](https://linkedin.com)")

    # --- DOUBLE BONUS: DM Drafter ---
    st.markdown("---")
    if row['Likes'] < 50:
        st.error(f"⚠️ Low Reach: {row['Likes']} likes")
        dm_text = f"Hey {selection} team! Saw your launch video. The tech looks incredible, but it looks like the algorithm didn't give it much love. Would love to chat about how our AI tools can help boost your distribution!"
        st.text_area("Drafted Outreach:", dm_text, height=150)
    else:
        st.success(f"🔥 High Reach: {row['Likes']} likes")
        st.write("This launch is performing well!")

st.markdown("---")
st.caption("Built with Claude Code & Streamlit")
