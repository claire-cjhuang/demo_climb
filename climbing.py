import datetime
import os
from io import BytesIO

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
        return pd.DataFrame(columns=["Date", "Grade", "Type", "Style", "Difficulty"])

# Function to save the logbook data to the CSV file
def save_logbook(df):
    df['Date'] = df['Date'].astype(str)
    df.to_csv(LOGBOOK_FILE, index=False)

# Function to convert DataFrame to CSV file for downloading
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Initialize logbook data
logbook_df = load_logbook()

# App title
st.title("Coolcat's Climbing App with Viz")

# Input fields for log entry
with st.form("log_entry_form", clear_on_submit=True):
    # Date picker
    date = st.date_input("Date")
    
    # Grade selection (V1 to V7), default is "V4"
    grade = st.selectbox("Grade", ["V1", "V2", "V3", "V4", "V5", "V6", "V7"], index=3)  # Default to "V4"
    
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
    
    # Submit button
    submitted = st.form_submit_button("Add Entry")

    # Save data when form is submitted
    if submitted:
        # If "Other" style was entered, add it to the Style column
        if other_style:
            style = [s if s != "Other" else other_style for s in style]

        # Add the new entry to the logbook dataframe
        new_entry = {
            "Date": date,
            "Grade": grade,
            "Type": type_climb,
            "Style": ", ".join(style),  # Combine styles into a string
            "Difficulty": difficulty
        }
        logbook_df = logbook_df.append(new_entry, ignore_index=True)
        
        # Save the updated logbook to CSV
        save_logbook(logbook_df)

        st.success("Entry added!")


# Display logbook data
st.subheader("Logbook Entries")
if not logbook_df.empty:
    st.dataframe(logbook_df)

    # Option to edit or delete a record (hidden by default)
    show_edit_delete_form = st.checkbox("Edit or Delete an Entry")

    if show_edit_delete_form:
        selected_entry = st.selectbox("Select an entry to edit or delete", logbook_df.index)

        if selected_entry is not None:
            entry_to_edit = logbook_df.iloc[selected_entry]

            # Display the selected entry details for editing
            with st.form("edit_form", clear_on_submit=True):
                st.write(f"Editing Entry: {entry_to_edit['Date']} - {entry_to_edit['Grade']}")

                # Ensure the Date value is of type datetime.date for the date picker
                date_edit = st.date_input("Date", pd.to_datetime(entry_to_edit['Date']).date())
                grade_edit = st.selectbox("Grade", ["V1", "V2", "V3", "V4", "V5", "V6", "V7"], index=["V1", "V2", "V3", "V4", "V5", "V6", "V7"].index(entry_to_edit['Grade']))
                type_climb_edit = st.selectbox("Type", ["Vertical", "Slab", "Overhang", "Cave"], index=["Vertical", "Slab", "Overhang", "Cave"].index(entry_to_edit['Type']))
                style_edit = st.multiselect("Style", ["Jug", "Pinch", "Crimp", "Compression", "Dyno", "Side Pull", "Sloper", "Undercling", "Other"], default=entry_to_edit['Style'].split(", "))
                other_style_edit = ""
                if "Other" in style_edit:
                    other_style_edit = st.text_input("Other Style", entry_to_edit['Style'].split(", ")[-1] if "Other" in entry_to_edit['Style'] else "")

                difficulty_edit = st.selectbox("Difficulty", ["Flash", "Quick Send", "Project"], index=["Flash", "Quick Send", "Project"].index(entry_to_edit['Difficulty']))
                
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

                    # Save the updated logbook to CSV
                    save_logbook(logbook_df)
                    st.success("Entry updated!")

            # Option to delete the entry
            if st.button("Delete Selected Entry"):
                logbook_df = logbook_df.drop(selected_entry).reset_index(drop=True)
                save_logbook(logbook_df)
                st.success("Entry deleted!")
else:
    st.info("No entries yet. Add some!")
    
# Download button for CSV
csv = convert_df_to_csv(logbook_df)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="climbing_logbook.csv",
    mime="text/csv"
)


# Simple Viz of Sends
st.subheader("Simple Viz of Sends")

# Convert logbook dates to datetime.date type if necessary
if not logbook_df.empty:
    logbook_df['Date'] = pd.to_datetime(logbook_df['Date']).dt.date

# Filter data for the current month
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year
logbook_df['Month'] = pd.to_datetime(logbook_df['Date']).dt.month
logbook_df['Year'] = pd.to_datetime(logbook_df['Date']).dt.year

# Filter for entries in the current month
monthly_entries = logbook_df[(logbook_df['Month'] == current_month) & (logbook_df['Year'] == current_year)]

# Count entries by Grade and Difficulty
if not monthly_entries.empty:
    # Group by Grade and Difficulty and count the entries
    grade_difficulty_counts = monthly_entries.groupby(['Grade', 'Difficulty']).size().unstack(fill_value=0)

    # Plotting using Matplotlib
    ax = grade_difficulty_counts.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set3')

    # Set plot labels and title
    ax.set_xlabel('Grade')
    ax.set_ylabel('Number of Entries')
    ax.set_title('Climbing Logbook: Current Month Entries by Grade and Difficulty')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(title="Difficulty", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Show the plot
    st.pyplot(ax.figure)

else:
    st.info("No entries for the current month. Add some entries!")