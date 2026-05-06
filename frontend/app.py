# frontend/app.py
import streamlit as st
import requests

# Set up the page layout
st.set_page_config(page_title="Review Insights API", page_icon="📊", layout="centered")

st.title("📊 Amazon Review Insights Dashboard")
st.markdown("Ask natural language questions about product reviews and get AI-generated summaries.")

# The input box for the user
query = st.text_input(
    "What would you like to know?", 
    placeholder="e.g., What are the common complaints about screen glare?"
)

# The trigger button
if st.button("Analyze Reviews"):
    if query.strip():
        # Show a loading spinner while the backend does the heavy lifting
        with st.spinner("AI is reading the reviews... Please wait."):
            try:
                # Send the POST request to your FastAPI server
                response = requests.post(
                    "https://amazon-rag-api.onrender.com/analyze",  # <--- Your live Render URL!
                    json={"query": query}
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete!")
                    st.markdown("### AI Analyst Report")
                    st.write(data["answer"])
                else:
                    st.error(f"Backend API Error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend. Is your FastAPI server running on port 8000?")
    else:
        st.warning("Please enter a question first.")