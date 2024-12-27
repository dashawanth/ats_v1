import streamlit as st
from utils.data_loader import load_data
from utils.recruiter_page import recruiter_page
from utils.jobs_page import jobs_page
from utils.submissions_page import submissions_page
from utils.single_page import single_page
from utils.path_page import path_to_file
from utils.dashboard import dashboard
from utils.ATS_Score import process_resumes



def main():
    st.set_page_config(layout="wide")

    st.title("Recruitment Management Dashboard")
    
    recruiter_detail, job_requirements, submission_table = load_data()

    tabs = st.tabs(["Dashboard","Recruiter", "Jobs", "Submissions", "Single", "Folder Path","ATS Score"])
    
    with tabs[0]:
        dashboard(recruiter_detail, job_requirements, submission_table)


    with tabs[1]:
        recruiter_page(recruiter_detail)
        
    with tabs[2]:
        jobs_page(job_requirements)
        
    with tabs[3]:
        submissions_page(submission_table)
    
    with tabs[4]:
        single_page()
    
    with tabs[5]:
        path_to_file()
        
    with tabs[6]:
        process_resumes()
        

if __name__ == "__main__":
    main()


