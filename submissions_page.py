import streamlit as st
import pandas as pd

def submissions_page(submission_table):
    st.header("Submission Table")

    # Search functionality
    search_term = st.text_input("Search by Client Name:")
    filtered_df_search = submission_table[
        submission_table["Client_Name"].str.contains(search_term, case=False, na=False)
    ]

    with st.expander("Submission Table", expanded=bool(search_term)):
        st.dataframe(filtered_df_search, hide_index=True, use_container_width=True)

    # Radio button to toggle between options
    action = st.radio(
        "Choose Action:",
        options=["Edit Notes for a Submission", "Add a New Submission", "Remove submission"]
    )

    if action == "Edit Notes for a Submission":
        st.subheader("Edit Notes for a Submission")

        job_ids = filtered_df_search["Job_Id"].tolist()
        job_ids.insert(0, "Select Job ID")  # Add placeholder

        selected_job_id = st.selectbox("Select Job ID to Edit Notes:", job_ids)

        if selected_job_id != "Select Job ID":
            selected_job_id = int(selected_job_id)
            current_notes = submission_table.loc[
                submission_table["Job_Id"] == selected_job_id, "Notes"
            ].values[0] if not submission_table.loc[
                submission_table["Job_Id"] == selected_job_id, "Notes"
            ].empty else ""

            new_notes = st.text_area("Update Notes:", value=current_notes)

            if st.button("Save Notes"):
                submission_table.loc[
                    submission_table["Job_Id"] == selected_job_id, "Notes"
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
                    "Job_Id": int(submission_table["Job_Id"].max() + 1),
                    "Date_of_Submission": new_date,
                    "Client_Name": new_client_name,
                    "Job_Title": new_job_title,
                    "Candidate_City": new_candidate_city,
                    "Candidate_State": new_candidate_state,
                    "Candidate_Country": new_candidate_country,
                    "Visa": new_visa,
                    "Recruiter": new_recruiter,
                    "Pay_Rate": new_pay_rate,
                    'Status': new_status,
                    "Notes": new_notes,
                }
                submission_table = pd.concat(
                    [submission_table, pd.DataFrame([new_row])], ignore_index=True
                )
                submission_table.to_csv('s3://ats-files1/data/submission_table.csv', index=False)
                st.success("New submission added successfully!")
                st.session_state.updated = True

    elif action == "Remove submission":
        st.subheader("Remove a Submission")

        job_ids = filtered_df_search["Job_Id"].tolist()
        job_ids.insert(0, "Select Job ID")  # Add placeholder

        selected_job_id = st.selectbox("Select Job ID to Remove:", job_ids)

        if selected_job_id != "Select Job ID" and st.button("Remove Submission"):
            selected_job_id = int(selected_job_id)
            submission_table = submission_table[submission_table["Job_Id"] != selected_job_id]
            submission_table.to_csv('s3://ats-files1/data/submission_table.csv', index=False)  # Save changes to CSV
            st.success(f"Submission with Job ID {selected_job_id} removed successfully!")
            st.session_state.updated = True  # Set session state to trigger a refresh


# Load data from CSV
def load_submission_data(filepath):
    try:
        data = pd.read_csv(filepath)
        data["Job_Id"] = data["Job_Id"].astype(int)  # Ensure job_id is integer
        return data
    except FileNotFoundError:
        st.warning("File not found. Starting with an empty dataset.")
        return pd.DataFrame(columns=[
            "Job_Id", "Date_of_Submission", "Client_Name", "Job_Title",
            "Candidate_City", "Candidate_State", "Candidate_Country",
            "Visa", "Recruiter", "Pay_Rate", "Notes"
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
