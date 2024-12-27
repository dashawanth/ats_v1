import streamlit as st  # Streamlit is an open-source app framework for Machine Learning and Data Science teams. It allows you to create and share beautiful, custom web apps for data science and machine learning.
import google.generativeai as genai  # Google GenAI is an AI platform that provides a suite of AI models and a no-code interface for generating code, text, and other content.
import os  # The OS module in Python provides a way of using operating system dependent functionality.
import PyPDF2 as pdf  # PyPDF2 is a Python library used for reading and writing PDF files.
from dotenv import load_dotenv  # Load environment variables from a .env file into os.environ.
import pandas as pd  # Pandas is a library used for data manipulation and analysis.
import docx2txt  # Docx2txt is a library used to convert .docx files to text.
import re  # The re library provides support for regular expressions in Python.
import time  # The time library provides various time-related functions.
load_dotenv()

def single_page():

    # Load all environment variables
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_gemini_response(input_text, file_content, prompt):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([input_text, file_content, prompt])
        return response.text 

    def input_pdf_text(uploaded_file):
        if uploaded_file is not None:
            reader = pdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    def input_doc_text(uploaded_file):
        if uploaded_file is not None:
            text = docx2txt.process(uploaded_file)
            return text 
        else:
            raise FileNotFoundError("No file uploaded")
        
    def save_to_csv(data, filename="resume_output.csv"):
        df = pd.DataFrame(data)  # Convert the data to a DataFrame
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)  # Append to existing file
        else:
            df.to_csv(filename, mode='w', header=True, index=False)

    # Streamlit App
    st.header("Smart ATS")
    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)...", type=["pdf", "docx"])

    if uploaded_file is not None:
        st.write("File Uploaded Successfully")

    submit2 = st.button("Get Percentage")
    submit1 = st.button("Submit")

    input_prompt1 = """
        You are a highly skilled ATS (Applicant Tracking System) specializing in resume parsing. Extract the following details from the provided resume text carefully, focusing only on valid USA and India phone numbers.

        1. **Name:** The candidate's full name, typically at the top of the resume.
        2. **Phone Number:** Extract only valid phone numbers in the following formats:  
        - **USA**: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX  
        - **India**: +91-XXXXX-XXXXX or XXXXX-XXXXX
        3. **Email ID:** A valid email format (e.g., example@example.com).
        4. **Job Title:** The most recent or current job title.
        5. **Current Company:** The company the candidate is currently or most recently employed with.
        6. **Skills:** A list of skills mentioned, separated by commas.
        7. **Location:** City, state, or region where the candidate is based.

        ### Dos:  
        - Extract USA phone numbers in the format: +1-XXX-XXX-XXXX or (XXX) XXX-XXXX.  
        - Extract India phone numbers in the format: +91-XXXXX-XXXXX or XXXXX-XXXXX.  
        - Look for the candidate’s full name at the top of the resume, using title case (e.g., "John Doe").  
        - Ensure emails include an `@` symbol and a valid domain (e.g., example@example.com).  
        - Identify job titles and current company names under "Experience" or "Work History."  
        - Extract technical and soft skills explicitly listed in the resume, separated by commas.  
        - Identify the candidate’s location as the city, state, or country, avoiding company addresses.  

        ### Don’ts:  
        - Don’t extract phone numbers that don’t match valid USA or India formats.  
        - Don’t assume the first word in the document is the name if it doesn't follow title case.  
        - Avoid incomplete or malformed email addresses with spaces or special characters.  
        - Don’t extract outdated job titles if current ones are available.  
        - Avoid capturing irrelevant numeric strings as phone numbers.  
        - Don’t include generic terms like “communication skills” unless explicitly listed.  
        - Ensure the location isn’t mistaken for company headquarters.

        ### Resume:
        {text}

        **Output Format:**  

        Please provide the response as a single string formatted as follows:  
        Name: [value or 'Null'],  
        Phone Number: [value or 'Null'],  
        Email ID: [value or 'Null'],  
        Job Title: [value or 'Null'],  
        Current Company: [value or 'Null'],  
        Skills: [list of values or 'Null'],  
        Location: [value or 'Null']  

        Ensure all fields are filled accurately or marked as 'Null' if missing.
    """

    input_prompt2 = """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
    Your task is to evaluate the resume against the provided job description. 
    Give me the percentage of match if the resume matches the job description. 
    First, the output should come as percentage, then keywords missing, and finally final thoughts.
    """

    if submit1:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                text = input_pdf_text(uploaded_file)
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for percent_complete in range(100):
                    time.sleep(0.05)  # Simulate processing time
                    progress_bar.progress(percent_complete + 1)
                    progress_text.text(f"Processing {uploaded_file.name}: {percent_complete + 1}% completed")
                file_content = input_pdf_text(uploaded_file)
                response = get_gemini_response(input_text, file_content, input_prompt1)
            elif uploaded_file.name.endswith('.docx'):
                text = input_doc_text(uploaded_file)
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for percent_complete in range(100):
                    time.sleep(0.05)  # Simulate processing time
                    progress_bar.progress(percent_complete + 1)
                    progress_text.text(f"Processing {uploaded_file.name}: {percent_complete + 1}% completed")
                file_content = input_doc_text(uploaded_file)
                response = get_gemini_response(input_text, file_content, input_prompt1)

            st.subheader("The Response is:")
            response = re.sub(r"'", '"', response)  # Replace single quotes with double quotes
            response = response.replace('\n', ' ')  # Replace newlines with a space
            #st.write("Raw Response:", response)  # Debug print
            
            # Extract data using regex
            name = re.search(r"Name:\s*(.*?)(,|$)", response)
            phone = re.search(r"Phone Number:\s*(.*?)(,|$)", response)
            email = re.search(r"Email ID:\s*(.*?)(,|$)", response)
            job_title = re.search(r"Job Title:\s*(.*?)(,|$)", response)
            current_company = re.search(r"Current Company:\s*(.*?)(,|$)", response)
            skills_match = re.search(r"(?:Skills|Technologies Used):\s*(.*?)(?=\s(?:Location|Phone Number|$))", response, re.IGNORECASE)
            location = re.search(r"Location:\s*(.*?)(,|$)", response)

            # Prepare data dictionary
            data = {
                'Name': name.group(1).strip() if name else 'Null',
                'Phone Number': phone.group(1).strip() if phone else 'Null',
                'Email ID': email.group(1).strip() if email else 'Null',
                'Job Title': job_title.group(1).strip() if job_title else 'Null',
                'Current Company': current_company.group(1).strip() if current_company else 'Null',
                'Skills': skills_match.group(1).strip() if skills_match else 'Null',
                'Location': location.group(1).strip() if location else 'Null'
            }
            
            # Create a DataFrame with a single row
            df = pd.DataFrame([data])  # Convert the data to a DataFrame with a single row
            st.write(df[['Name', 'Phone Number', 'Email ID', 'Job Title', 'Skills']], hide_index=True, use_container_width=True)  # Display the DataFrame
            try:
                save_to_csv([data], filename=r"s3://ats-files1/data/resume_output.csv")  # Use raw string to handle backslashes
            except OSError as e:
                st.error(f"Failed to save to CSV: {e}")
            
        else:
            st.write("Please upload the resume")

    elif submit2:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                pdf_content = input_pdf_text(uploaded_file)
                response = get_gemini_response(input_prompt2, pdf_content, input_text)
            elif uploaded_file.name.endswith('.docx'):
                doc_content = input_doc_text(uploaded_file)
                response = get_gemini_response(input_prompt2, doc_content, input_text)
            st.subheader("The Response is:")
            st.write(response)
        else:
            st.write("Please upload the resume")

