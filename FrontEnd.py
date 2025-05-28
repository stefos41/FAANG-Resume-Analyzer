import streamlit as st
from rag import FAANGJobAnalyzer
from scrapper import scrape_faang_jobs
import json
import PyPDF2 

# Initialize
analyzer = FAANGJobAnalyzer()
jobs = scrape_faang_jobs()
analyzer.load_jobs(jobs)

# UI
st.title("🔍 FAANG Resume Optimizer (OpenAI)")
uploaded_file = st.file_uploader("Upload Resume (PDF/TXT)")

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        resume_text = "\n".join([page.extract_text() for page in reader.pages])
        
    else:
        resume_text = uploaded_file.read().decode() 


    analysis = analyzer.analyze(resume_text)

    # Display results
    st.subheader("📊 Match Score")
    st.metric("Overall", f"{analysis['score']}/100")

    st.subheader("🚀 Actionable Advice")
    for item in analysis["advice"]:
        st.markdown(f"- {item}")