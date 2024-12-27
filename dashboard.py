import streamlit as st


def dashboard(recruiter_detail, job_requirements, submission_table):

    st.header('Summary Report')
    ttotal_recruiter = recruiter_detail.shape[0]
    total_jobs = job_requirements.shape[0]
    total_submission = submission_table.shape[0]

    total1 , total2,total3 = st.columns(3, gap='small')

    with total1:
        st.info('Total Recruiters', icon="👨‍💼")
        st.metric(label="Recruiters Count", value=f'{ttotal_recruiter}', label_visibility="collapsed")
    with total2:
        st.info('Total Jobs', icon="📋")
        st.metric(label="Jobs Count", value=f'{total_jobs}', label_visibility="collapsed")
    with total3:
        st.info('Total Submission', icon="📤")
        st.metric(label="Submissions Count", value=f'{total_submission}', label_visibility="collapsed")


