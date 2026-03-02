import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Launch Dashboard", layout="wide")

st.title("🚀 AI Launch & Fundraising Dashboard")
st.write("Tracking recent launches and engagement metrics.")

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv('launches.csv')

try:
    df = load_data()
    
    # Dashboard Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Launch Data")
        # Add random placeholder data for the assessment
        df['Funding'] = "$2M - $10M"
        df['Likes'] = [12, 85, 4, 120, 30] # Examples
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("Action Center")
        selection = st.selectbox("Select a Company to Analyze", df['Company_Name'])
        
        # Bonus: Enrichment Box
        st.info(f"**Contact Info for {selection}**\n\n📧 founder@example.com\n📞 +1-555-0199")
        
        # Double Bonus: DM Generator
        company_likes = df[df['Company_Name'] == selection]['Likes'].values[0]
        if company_likes < 50:
            st.warning("⚠️ Low Engagement Detected")
            dm_draft = f"Hey {selection} team! Saw your launch video. The product looks great, but noticed it didn't get much reach on X. Would love to chat about how AI can help boost your distribution!"
            st.text_area("Drafted DM:", dm_draft, height=150)
        else:
            st.success("✅ Strong Launch Engagement")

except Exception as e:
    st.error("Please ensure 'launches.csv' is created and has 'Company_Name' and 'Launch_URL' columns.")
