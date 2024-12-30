import streamlit as st
import pandas as pd

def submissions_page(submission_table):
    st.header("Submission Table")

    # Search functionality
    search_term = st.text_input("Search by Client Name:")
    filtered_df_search = submission_table[
        submission_table["client_name"].str.contains(search_term, case=False, na=False)
    ]

    with st.expander("Submission Table"):
        st.dataframe(filtered_df_search,hide_index=True, use_container_width=True)

    # Radio button to toggle between options
    action = st.radio(
        "Choose Action:",
        options=["Edit Notes for a Submission", "Add a New Submission", "Remove submission"]
    )

    if action == "Edit Notes for a Submission":
        st.subheader("Edit Notes for a Submission")

        job_ids = filtered_df_search["job_id"].tolist()
        job_ids.insert(0, "Select a Job ID")  # Add placeholder

        selected_job_id = st.selectbox("Select Job ID to Edit Notes:", job_ids)

        if selected_job_id != "Select a Job ID":
            current_notes = submission_table.loc[
                submission_table["job_id"] == selected_job_id, "notes"
            ].values[0] if not submission_table.loc[
                submission_table["job_id"] == selected_job_id, "notes"
            ].empty else ""

            new_notes = st.text_area("Update Notes:", value=current_notes)

            if st.button("Save Notes"):
                submission_table.loc[
                    submission_table["job_id"] == selected_job_id, "notes"
                ] = new_notes
                submission_table.to_csv('s3://ats-files1/data/submission_table.csv', index=False)
                st.success(f"Notes updated for Job ID {selected_job_id}!")
                st.session_state.updated = True  # Set session state to trigger a refresh

    elif action == "Add a New Submission":
        st.subheader("Add a New Submission")

        with st.form("add_submission_form"):
            new_date = st.date_input("Date of Submission:")
            new_client_name = st.text_input("Client Name:")
            new_job_title = st.text_input("Job Title:")
            new_candidate_city = st.text_input("Candidate City:")
            new_candidate_state = st.text_input("Candidate State:")
            new_candidate_country = st.text_input("Candidate Country:")
            new_visa = st.text_input("Visa:")
            new_recruiter = st.text_input("Recruiter:")
            new_pay_rate = st.text_input("Pay Rate:")
            new_status = st.multiselect("Status:", ["Initial discussion", "Interview", "Submitted", 'Selected'])
            new_notes = st.text_area("Notes:")

            submitted = st.form_submit_button("Add Submission")
            if submitted:
                new_row = {
                    "job_id": submission_table["job_id"].max() + 1,
                    "date_of_submission": new_date,
                    "client_name": new_client_name,
                    "job_title": new_job_title,
                    "candidate_city": new_candidate_city,
                    "candidate_state": new_candidate_state,
                    "candidate_country": new_candidate_country,
                    "visa": new_visa,
                    "recruiter": new_recruiter,
                    "pay_rate": new_pay_rate,
                    'status': new_status,
                    "notes": new_notes,
                }
                submission_table = pd.concat(
                    [submission_table, pd.DataFrame([new_row])], ignore_index=True
                )
                submission_table.to_csv('s3://ats-files1/data/submission_table.csv', index=False)
                st.success("New submission added successfully!")
                st.session_state.updated = True

    elif action == "Remove submission":
        st.subheader("Remove a Submission")

        job_ids = filtered_df_search["job_id"].astype(int).tolist()
        job_ids.insert(0, "Select a Job ID")  # Add placeholder

        selected_job_id = st.selectbox("Select Job ID to Remove:", job_ids)

        if selected_job_id != "Select a Job ID" and st.button("Remove Submission"):
            submission_table = submission_table[submission_table["job_id"] != selected_job_id]
            submission_table.to_csv('s3://ats-files1/data/submission_table.csv', index=False)  # Save changes to CSV
            st.success(f"Submission with Job ID {selected_job_id} removed successfully!")
            st.session_state.updated = True  # Set session state to trigger a refresh

# Load data from CSV
def load_submission_data(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        st.warning("File not found. Starting with an empty dataset.")
        return pd.DataFrame(columns=[
            "job_id", "date_of_submission", "client_name", "job_title",
            "candidate_city", "candidate_state", "candidate_country",
            "visa", "recruiter", "pay_rate", "notes"
        ])

# Main execution
def main():
    # Initialize session state for updates if it doesn't exist
    if "updated" not in st.session_state:
        st.session_state.updated = False

    filepath = 's3://ats-files1/data/submission_table.csv'
    submission_table = load_submission_data(filepath)

    # Refresh the page when the state is updated
    if st.session_state.updated:
        st.session_state.updated = False
        st.experimental_rerun()  # Trigger a rerun to reflect the changes

    submissions_page(submission_table)

if __name__ == "__main__":
    main()
