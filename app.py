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
        df = pd.read_csv('launches.csv')
        df.columns = df.columns.str.strip()
        # Ensure required columns exist
        if 'Company_Name' not in df.columns:
            raise ValueError("Missing 'Company_Name' column in CSV")
        return df
    except Exception as e:
        st.warning(f"Could not load launches.csv ({e}). Using backup data.")
        backup_data = {
            'Company_Name': ['Captions', 'Perplexity', 'YCombinator', 'OpenAI', 'Anthropic'],
            'Launch_URL': ['https://x.com/1', 'https://x.com/2', 'https://x.com/3', 'https://x.com/4', 'https://x.com/5']
        }
        return pd.DataFrame(backup_data)

def fix_arrow_dtypes(df):
    """Convert LargeUtf8/large_string columns to standard string (Utf8).
    Fixes 'Unrecognized type: LargeUtf8' error in Streamlit's Arrow serializer."""
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or str(df[col].dtype) in ('large_string', 'string[large]'):
            df[col] = df[col].astype(str)
    return df

df = fix_arrow_dtypes(load_data())

# 3. Add Metric Columns (Dynamically scales to match all rows)
if 'Likes' not in df.columns:
    df['Likes'] = np.random.randint(5, 500, size=len(df))
else:
    # FIX: ensure Likes is numeric (prevents type errors later)
    df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce').fillna(0).astype(int)

if 'Funding' not in df.columns:
    funding_options = ["$1M", "$5M", "$10M", "$25M", "$50M", "$100M"]
    df['Funding'] = [np.random.choice(funding_options) for _ in range(len(df))]

# 4. Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Launch Engagement Tracker")
    st.dataframe(fix_arrow_dtypes(df.copy()), use_container_width=True)

    # FIX: guard against missing/duplicate Company_Name before charting
    chart_df = df[['Company_Name', 'Likes']].dropna().drop_duplicates('Company_Name')
    st.bar_chart(chart_df.set_index('Company_Name')['Likes'])

with col2:
    st.subheader("🎯 Action Center")
    company_list = df['Company_Name'].dropna().tolist()
    selection = st.selectbox("Select a Company to Enrich:", company_list)

    row = df[df['Company_Name'] == selection].iloc[0]

    # FIX: use st.markdown for proper rendering of bold/links
    st.markdown(
        f"**Enriched Contact Methods**\n\n"
        f"📧 **Email:** info@{selection.lower().replace(' ', '')}.ai\n\n"
        f"🔗 [View LinkedIn Profile](https://linkedin.com)\n\n"
        f"💰 **Funding Round:** {row['Funding']}"
    )

    st.markdown("---")
    likes = int(row['Likes'])  # FIX: explicit cast prevents comparison type errors
    if likes < 50:
        st.error(f"⚠️ Low Reach: {likes} likes")
        dm_text = (
            f"Hey {selection} team! Saw your launch video. The tech looks incredible, "
            f"but it looks like the algorithm didn't give it much love. Would love to chat "
            f"about how our AI tools can help boost your distribution!"
        )
        st.text_area("Drafted Outreach:", dm_text, height=150)
    else:
        st.success(f"🔥 High Reach: {likes} likes")
        st.write("This launch is performing well!")

st.markdown("---")
st.caption("Built with Claude & Streamlit")
