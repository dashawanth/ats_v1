import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import docx2txt
import re
import time
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def process_resumes():
    st.header("ATS Score")

    # Inputs
    job_description = st.text_area("Enter Job Description:")
    match_target = st.number_input("Enter Match Percentage Target (0-100):", min_value=0, max_value=100, step=1)
    resumes_path = st.text_input("Enter the Path to the Resumes Folder:")

    if st.button("Process Resumes"):
        if not job_description or not resumes_path:
            st.error("Please provide both job description and resumes folder path.")
            return

        matching_emails = []
        resume_data = []  # For storing extracted information

        files = [f for f in os.listdir(resumes_path) if f.endswith(('.pdf', '.docx'))]

        if not files:
            st.warning("No resumes found in the specified folder.")
            return

        # Initialize progress bar
        total_files = len(files)
        progress_bar = st.progress(0)
        progress_text = st.empty()

        for i, file_name in enumerate(files):
            file_path = os.path.join(resumes_path, file_name)
            progress_text.text(f"Processing file {i+1}/{total_files}: {file_name}")

            # Extract text from resumes
            if file_name.endswith('.pdf'):
                reader = pdf.PdfReader(file_path)
                file_content = "".join(page.extract_text() or "" for page in reader.pages)
            elif file_name.endswith('.docx'):
                file_content = docx2txt.process(file_path)

            # Generate Gemini response for percentage match
            input_prompt = f"""
            You are an advanced Applicant Tracking System (ATS). Your job is to analyze the following resume and compare it with the provided job description. Perform the following tasks in a structured manner:

            ### Task 1: Extract Details from the Resume
            1. **Candidate Name**: Identify and extract the candidate's full name.
            2. **Email Address**: Extract the candidate's email address (including Gmail).
            3. **Skills**: Extract all listed skills from the resume.

            ### Task 2: Evaluate Match with Job Description
            1. **Match Percentage**: Calculate the match percentage by comparing the candidate's skills with the skills mentioned in the job description. Only consider unique and relevant skills.
            2. **Missing Keywords**: List the skills that are present in the job description but missing from the resume.

            ### Task 3: Summary of Evaluation
            Provide a concise summary that includes:
            1. Candidate's Name
            2. Match Percentage
            3. Missing Keywords (if any)
            4. A final comment on the overall match.

            ### Important Note:
            Only include this candidate if the match percentage meets or exceeds the target specified by the user.

            **Job Description:**
            {job_description}

            **Resume Content:**
            {file_content}
            """
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content([input_prompt]).text

            # Extract match percentage using regex
            match_percentage = re.search(r"Match Percentage:\s*(\d+)", response)
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", file_content)
            name_match = re.search(r"Candidate Name:\s*(.*?)(,|$)", response)
            

            if match_percentage:
                percentage = int(match_percentage.group(1))
                if percentage >= match_target and email_match:
                    email = email_match.group()
                    candidate_name = name_match.group(1).strip() if name_match else "N/A"
                    matching_emails.append(email)
                    resume_data.append({"Name": candidate_name, "Email": email, "Match Percentage": percentage})

            # Update progress bar based on processed files
            progress_bar.progress((i + 1) / total_files)

        progress_bar.empty()
        progress_text.empty()

        # Display download button for matching emails in CSV format
        if matching_emails:
            df = pd.DataFrame(resume_data)
            csv_data = df.to_csv(index=False)
            st.download_button("Download Matching Resumes CSV", csv_data, file_name="matching_resumes.csv", mime="text/csv")
        else:
            st.warning("No resumes matched the specified percentage target.")


if __name__ == "__main__":
    process_resumes()
