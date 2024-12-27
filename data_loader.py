import pandas as pd

def load_data():
    recruiter_detail = pd.read_csv('s3://ats-files1/data/recruiter_detail.csv')
    job_requirements = pd.read_csv('s3://ats-files1/data/job_requirements.csv')
    submission_table = pd.read_csv('s3://ats-files1/data/submission_table.csv')
    return recruiter_detail, job_requirements, submission_table
