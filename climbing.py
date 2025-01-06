import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.ticker import MaxNLocator

# File path to store the logbook data
LOGBOOK_FILE = "logbook_data.csv"

# Function to load the logbook data from the CSV file (if it exists)
def load_logbook():
    if os.path.exists(LOGBOOK_FILE):
        df = pd.read_csv(LOGBOOK_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date 
        return df
    else:
        return pd.DataFrame(columns=["Date", "Grade", "Type", "Style", "Difficulty", "Username", "Climb Name"])

# Function to save the logbook data to the CSV file (filter by username)
def save_logbook(df, username):
    # Filter the dataframe to include only entries that match the username
    user_logbook_df = df[df['Username'] == username]
    user_logbook_df['Date'] = user_logbook_df['Date'].astype(str)  # Ensure dates are strings
    user_logbook_df.to_csv(LOGBOOK_FILE, index=False)

# Function to convert DataFrame to CSV file for downloading (filtered by username)
def convert_df_to_csv(df, username):
    # Filter to include only the current user's data
    user_logbook_df = df[df['Username'] == username]
    return user_logbook_df.to_csv(index=False).encode('utf-8')

# Initialize logbook data
logbook_df = load_logbook()

# App title
st.title("Coolcat's Climbing App with Viz")

# Input fields for username at the start of the app
username = st.text_input("Enter your username")

# If the user provides a username, proceed with the form and logbook functionality
if username:
    # Check if this is the first time the user is logging in
    if username not in logbook_df['Username'].values:
        st.write(f"Welcome, {username}! It looks like this is your first logbook entry.")
    else:
        st.write(f"Welcome back, {username}!")

    # Filter the logbook to show only the current user's entries
    user_logbook_df = logbook_df[logbook_df['Username'] == username]

    # Input fields for log entry
    with st.form("log_entry_form", clear_on_submit=True):
        # Date picker
        date = st.date_input("Date")
        
        # Grade selection (V1 to V9), default is "V4"
        grade = st.selectbox("Grade", ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9"], index=3)  # Default to "V4"
        
        # Type selection (vertical, slab, overhang, cave)
        type_climb = st.selectbox("Type", ["Vertical", "Slab", "Overhang", "Cave"])
        
        # Style selection (multiple choices)
        style = st.multiselect(
            "Style", 
            ["Jug", "Pinch", "Crimp", "Compression", "Dyno", "Side Pull", "Sloper", "Undercling", "Other"],
            default=["Crimp"]
        )
        
        # If "Other" is selected, show a text input for custom style
        other_style = ""
        if "Other" in style:
            other_style = st.text_input("Other Style (if applicable)", "")

        # Difficulty selection (Flash, Quick Send, Project)
        difficulty = st.selectbox("Difficulty", ["Flash", "Quick Send", "Project"])

        # Climb name input (free text, default empty)
        climb_name = st.text_input("Climb Name (optional)", "")
        
        # Submit button
        submitted = st.form_submit_button("Add Entry")

        # Save data when form is submitted
        if submitted:
            # If "Other" style was entered, add it to the Style column
            if other_style:
                style = [s if s != "Other" else other_style for s in style]

            # Add the new entry to the logbook dataframe
            new_entry = pd.DataFrame([{
                "Date": date,
                "Grade": grade,
                "Type": type_climb,
                "Style": ", ".join(style),  # Combine styles into a string
                "Difficulty": difficulty,
                "Username": username,  # Add username to the log entry
                "Climb Name": climb_name 
            }])
            logbook_df = pd.concat([logbook_df, new_entry], ignore_index=True)
            
            # Save the updated logbook to CSV only for the current user
            save_logbook(logbook_df, username)
            st.success("Entry added!")

    # Display logbook data for the current user
    st.subheader("Your Logbook Entries")
    if not user_logbook_df.empty:
        st.dataframe(user_logbook_df)

        # Option to edit or delete a record (hidden by default)
        show_edit_delete_form = st.checkbox("Edit or Delete an Entry")

        if show_edit_delete_form:
            selected_entry = st.selectbox("Select an entry to edit or delete", user_logbook_df.index)

            if selected_entry is not None:
                entry_to_edit = user_logbook_df.iloc[selected_entry]

                # Display the selected entry details for editing
                with st.form("edit_form", clear_on_submit=True):
                    st.write(f"Editing Entry: {entry_to_edit['Date']} - {entry_to_edit['Grade']}")

                    # Ensure the Date value is of type datetime.date for the date picker
                    date_edit = st.date_input("Date", pd.to_datetime(entry_to_edit['Date']).date())
                    grade_edit = st.selectbox("Grade", ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9"], index=["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9"].index(entry_to_edit['Grade']))
                    type_climb_edit = st.selectbox("Type", ["Vertical", "Slab", "Overhang", "Cave"], index=["Vertical", "Slab", "Overhang", "Cave"].index(entry_to_edit['Type']))
                    style_edit = st.multiselect("Style", ["Jug", "Pinch", "Crimp", "Compression", "Dyno", "Side Pull", "Sloper", "Undercling", "Other"], default=entry_to_edit['Style'].split(", "))
                    other_style_edit = ""
                    if "Other" in style_edit:
                        other_style_edit = st.text_input("Other Style", entry_to_edit['Style'].split(", ")[-1] if "Other" in entry_to_edit['Style'] else "")

                    difficulty_edit = st.selectbox("Difficulty", ["Flash", "Quick Send", "Project"], index=["Flash", "Quick Send", "Project"].index(entry_to_edit['Difficulty']))
                    climb_name_edit = st.text_input("Climb Name", entry_to_edit['Climb Name'])
                    # Submit button for editing
                    edit_submitted = st.form_submit_button("Save Changes")

                    if edit_submitted:
                        # If "Other" style was entered, add it to the Style column
                        if other_style_edit:
                            style_edit = [s if s != "Other" else other_style_edit for s in style_edit]

                        # Update the entry in the DataFrame
                        logbook_df.loc[selected_entry, "Date"] = date_edit
                        logbook_df.loc[selected_entry, "Grade"] = grade_edit
                        logbook_df.loc[selected_entry, "Type"] = type_climb_edit
                        logbook_df.loc[selected_entry, "Style"] = ", ".join(style_edit)
                        logbook_df.loc[selected_entry, "Difficulty"] = difficulty_edit
                        logbook_df.loc[selected_entry, "Climb Name"] = climb_name_edit 

                        # Save the updated logbook to CSV only for the current user
                        save_logbook(logbook_df, username)
                        st.success("Entry updated!")

            # Option to delete the entry
            if st.button("Delete Selected Entry"):
                logbook_df = logbook_df.drop(selected_entry).reset_index(drop=True)
                # Ensure the CSV is saved only for the current user
                save_logbook(logbook_df, username)
                st.success("Entry deleted!")
    else:
        st.info("No entries yet. Add some!")


    # Download button for CSV for the current user
    csv = convert_df_to_csv(logbook_df, username)
    st.download_button(
        label="Download Your CSV",
        data=csv,
        file_name=f"{username}_climbing_logbook.csv",
        mime="text/csv"
    )


# Simple Viz of Sends
st.subheader("Simple Viz of Sends")
if not logbook_df.empty:
    # Filter for current user's data
    user_data = logbook_df[logbook_df['Username'] == username]

    # Ensure user_data is not empty
    if not user_data.empty:
        # Convert 'Date' column to datetime if necessary
        user_data['Date'] = pd.to_datetime(user_data['Date']).dt.date

        # Filter for current month and year
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        user_data['Month'] = pd.to_datetime(user_data['Date']).dt.month
        user_data['Year'] = pd.to_datetime(user_data['Date']).dt.year

        # Filter for entries in the current month
        monthly_entries = user_data[(user_data['Month'] == current_month) & (user_data['Year'] == current_year)]

        if not monthly_entries.empty:
            # Count entries by Grade and Difficulty
            grade_difficulty_counts = monthly_entries.groupby(['Grade', 'Difficulty']).size().unstack(fill_value=0)

            # Plotting using Matplotlib
            ax = grade_difficulty_counts.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set3')

            # Set plot labels and title
            ax.set_xlabel('Grade')
            ax.set_ylabel('Number of Entries')
            ax.set_title('Climbing Logbook: Current Month Entries by Grade and Difficulty')
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xticks(rotation=0, ha='center')
            ax.legend(title="Difficulty", bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Show the plot
            st.pyplot(ax.figure)

        else:
            st.info("No entries for the current month. Add some entries!")
    else:
        st.info(f"No data found for user: {username}. Add some entries!")
else:
    st.info("Logbook is empty. Add some entries!")