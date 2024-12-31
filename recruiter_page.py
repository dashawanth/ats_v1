import streamlit as st
import pandas as pd

def recruiter_page(recruiter_detail):
    st.header("Recruiter Details")

    # Search functionality to filter recruiters by recruiter_id
    search_term = st.text_input("Search by Recruiter ID:")

    # Filter data based on the search term
    filtered_df_search = recruiter_detail[
        recruiter_detail["Recruiter_Id"].astype(str).str.contains(search_term, case=False, na=False)
    ]

    # Automatically expand the expander if there is a search term
    with st.expander("Recruiter Details", expanded=bool(search_term)):
        st.dataframe(filtered_df_search, hide_index=True, use_container_width=True)

    # Radio buttons for selecting action
    action = st.radio(
        "Choose an Action:",
        options=["Edit Recruiter Details", "Add New Recruiter", "Remove Recruiter"],
    )

    if action == "Edit Recruiter Details":
        st.subheader("Edit Recruiter Details")

        # Dropdown menu to select a recruiter with an empty placeholder
        recruiter_ids = recruiter_detail["Recruiter_Id"].tolist()
        recruiter_ids.insert(0, "Select Recruiter ID")  # Add a placeholder option

        selected_recruiter_id = st.selectbox("Select Recruiter ID:", recruiter_ids)

        if selected_recruiter_id and selected_recruiter_id != "Select Recruiter ID":
            # Retrieve current details
            current_row = recruiter_detail[
                recruiter_detail["Recruiter_Id"] == selected_recruiter_id
            ].iloc[0]

            updated_name = st.text_input("Name:", value=current_row["Name"])
            updated_email = st.text_input("Email:", value=current_row["Email"])
            updated_phone_number = st.text_input("Phone Number:", value=current_row["Phone_Number"], max_chars=11)

            # Validate phone number format
            if len(updated_phone_number) == 10 and updated_phone_number.isdigit():
                updated_phone_number = f"{updated_phone_number[:3]}-{updated_phone_number[3:6]}-{updated_phone_number[6:]}"
            # elif len(updated_phone_number) != 12 or not updated_phone_number.replace("-", "").isdigit():
            #     st.warning("Please enter a valid 10-digit phone number in the format XXX-XXX-XXXX.")
            updated_location = st.text_input("Location:", value=current_row["Location"])
            updated_designation = st.text_input("Designation:", value=current_row["Designation"])

            if st.button("Save Changes"):
                # Update the details in the dataframe
                recruiter_detail.loc[
                    recruiter_detail["Recruiter_Id"] == selected_recruiter_id,
                    ["Name", "Email", "Phone_Number", "Location", "Designation"],
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
            new_phone_number = st.text_input("Phone Number:", max_chars=10)

            # Validate phone number format
            if len(new_phone_number) == 10 and new_phone_number.isdigit():
                new_phone_number = f"{new_phone_number[:3]}-{new_phone_number[3:6]}-{new_phone_number[6:]}"
            # elif len(new_phone_number) != 12 or not new_phone_number.replace("-", "").isdigit():
            #     st.warning("Please enter a valid 10-digit phone number in the format XXX-XXX-XXXX.")
            new_location = st.text_input("Location:")
            new_designation = st.text_input("Designation:")

            submitted = st.form_submit_button("Submit")
            if submitted:
                new_row = {
                    "Recruiter_Id": recruiter_detail["Recruiter_Id"].max() + 1,
                    "Name": new_name,
                    "Email": new_email,
                    "Phone_Number": new_phone_number,
                    "Location": new_location,
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
        recruiter_ids = recruiter_detail["Recruiter_Id"].tolist()
        recruiter_ids.insert(0, "Select Recruiter ID")  # Add a placeholder option

        selected_recruiter_id = st.selectbox("Select Recruiter ID to Remove:", recruiter_ids)

        if selected_recruiter_id and selected_recruiter_id != "Select Recruiter ID":
            if st.button("Remove Recruiter"):
                # Remove the selected recruiter
                recruiter_detail = recruiter_detail[
                    recruiter_detail["Recruiter_Id"] != selected_recruiter_id
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
                "Recruiter_Id",
                "Name",
                "Email",
                "Phone_Number",
                "Location",
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
