import streamlit as st
import pandas as pd

def recruiter_page(recruiter_detail):
    st.header("Recruiter Details")

    # Search functionality to filter recruiters by name
    search_term = st.text_input("Search by name:")

    # Filter data based on the search term
    filtered_df_search = recruiter_detail[
        recruiter_detail["name"].str.contains(search_term, case=False, na=False)
    ]

    with st.expander("Recruiter Details"):
        st.dataframe(filtered_df_search, hide_index=True, use_container_width=True)

    # Radio buttons for selecting action
    action = st.radio(
        "Choose an Action:",
        options=["Edit Recruiter Details", "Add New Recruiter", "Remove Recruiter"],
    )

    if action == "Edit Recruiter Details":
        st.subheader("Edit Recruiter Details")

        # Dropdown menu to select a recruiter with an empty placeholder
        recruiter_ids = recruiter_detail["recruiter_id"].tolist()
        recruiter_ids.insert(0, "Select a Recruiter ID")  # Add a placeholder option

        selected_recruiter_id = st.selectbox("Select Recruiter ID:", recruiter_ids)

        if selected_recruiter_id and selected_recruiter_id != "Select a Recruiter ID":
            # Retrieve current details
            current_row = recruiter_detail[
                recruiter_detail["recruiter_id"] == selected_recruiter_id
            ].iloc[0]

            updated_name = st.text_input("Name:", value=current_row["name"])
            updated_email = st.text_input("Email:", value=current_row["email"])
            updated_phone_number = st.text_input("Phone Number:", value=current_row["phone_number"])
            updated_location = st.text_input("Location:", value=current_row["location"])
            updated_designation = st.text_input("Designation:", value=current_row["Designation"])

            if st.button("Save Changes"):
                # Update the details in the dataframe
                recruiter_detail.loc[
                    recruiter_detail["recruiter_id"] == selected_recruiter_id,
                    ["name", "email", "phone_number", "location", "Designation"],
                ] = (
                    updated_name,
                    updated_email,
                    updated_phone_number,
                    updated_location,
                    updated_designation,
                )

                # Save the updated recruiter details back to the CSV file
                recruiter_detail.to_csv("s3://ats-files1/data/recruiter_detail.csv", index=False)

                st.success(f"Details updated for Recruiter ID {selected_recruiter_id}!")
                st.session_state.updated = True

    elif action == "Add New Recruiter":
        st.subheader("Add New Recruiter")

        # Form to add a new recruiter
        with st.form("add_recruiter_form"):
            #new_recruiter_id = st.text_input("Recruiter ID:")
            new_name = st.text_input("Name:")
            new_email = st.text_input("Email:")
            new_phone_number = st.text_input("Phone Number:")
            new_location = st.text_input("Location:")
            new_designation = st.text_input("Designation:")

            submitted = st.form_submit_button("Submit")
            if submitted:
                new_row = {
                    "recruiter_id": recruiter_detail["recruiter_id"].max() + 1,
                    "name": new_name,
                    "email": new_email,
                    "phone_number": new_phone_number,
                    "location": new_location,
                    "Designation": new_designation,
                }

                # Update the dataframe
                recruiter_detail = pd.concat(
                    [recruiter_detail, pd.DataFrame([new_row])], ignore_index=True
                )

                # Save the updated recruiter details back to the CSV file
                recruiter_detail.to_csv("s3://ats-files1/data/recruiter_detail.csv", index=False)

                st.success("New recruiter added successfully!")
                st.session_state.updated = True

    elif action == "Remove Recruiter":
        st.subheader("Remove Recruiter")

        # Dropdown menu to select a recruiter to remove with a placeholder option
        recruiter_ids = recruiter_detail["recruiter_id"].tolist()
        recruiter_ids.insert(0, "Select a Recruiter ID")  # Add a placeholder option

        selected_recruiter_id = st.selectbox("Select Recruiter ID to Remove:", recruiter_ids)

        if selected_recruiter_id and selected_recruiter_id != "Select a Recruiter ID":
            if st.button("Remove Recruiter"):
                # Remove the selected recruiter
                recruiter_detail = recruiter_detail[
                    recruiter_detail["recruiter_id"] != selected_recruiter_id
                ]

                # Save the updated recruiter details back to the CSV file
                recruiter_detail.to_csv("s3://ats-files1/data/recruiter_detail.csv", index=False)

                st.success(f"Recruiter ID {selected_recruiter_id} removed successfully!")
                st.session_state.updated = True
# Load data from CSV
def load_recruiter_data(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        st.warning("File not found. Starting with an empty dataset.")
        return pd.DataFrame(
            columns=[
                "recruiter_id",
                "name",
                "email",
                "phone_number",
                "location",
                "Designation",
            ]
        )

# Main execution
def main():
    # Initialize session state for updates if it doesn't exist
    if "updated" not in st.session_state:
        st.session_state.updated = False

    filepath = "s3://ats-files1/data/recruiter_detail.csv"
    recruiter_detail = load_recruiter_data(filepath)

    # Refresh functionality (optional)
    if st.session_state.updated:
        st.session_state.updated = False
        recruiter_detail = load_recruiter_data(filepath)

    recruiter_page(recruiter_detail)


if __name__ == "__main__":
    main()
