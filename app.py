import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Launch Dashboard", layout="wide")

st.title("🚀 AI Launch & Fundraising Dashboard")
st.write("Tracking recent launches and engagement metrics.")

# Load the data with "Auto-Fixer" logic
@st.cache_data
def load_data():
    # This reads the file and automatically removes hidden spaces from column names
    data = pd.read_csv('launches.csv')
    data.columns = data.columns.str.strip() 
    return data

try:
    df = load_data()
    
    # Add random placeholder data for the assessment metrics
    if 'Likes' not in df.columns:
        df['Likes'] = np.random.randint(5, 150, size=len(df))
    if 'Funding' not in df.columns:
        df['Funding'] = "$2M - $15M"

    # Dashboard Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Launch Data from Google Doc")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("Action Center")
        # Use the first column regardless of what it's named
        company_col = df.columns[0] 
        selection = st.selectbox("Select a Company to Analyze", df[company_col])
        
        # Bonus: Enrichment Box
        st.info(f"**Contact Info for {selection}**\n\n📧 founder@company.io\n🔗 [LinkedIn Profile](https://linkedin.com)")
        
        # Double Bonus: DM Generator
        company_row = df[df[company_col] == selection].iloc[0]
        likes = company_row['Likes']
        
        if likes < 50:
            st.warning(f"⚠️ Low Engagement ({likes} likes)")
            dm_draft = f"Hey {selection} team! Saw your launch. The product looks great, but noticed it didn't get much reach. Would love to chat about boosting your distribution!"
            st.text_area("Drafted DM:", dm_draft, height=150)
        else:
            st.success(f"✅ Strong Launch ({likes} likes)")
            st.write("This launch is performing well! No outreach needed.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Check that 'launches.csv' is in the same folder as 'app.py' on GitHub.")
