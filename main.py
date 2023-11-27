# main file for website

# to test: streamlit run c:/Code/ut_football_history/main.py
# Import convention
import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")

master_stats = pd.read_csv("master_stats_test.csv")
master_stats[['Year', 'Month', 'Day']] = master_stats['Date'].str.split('-', expand=True)

# Colunms
col1, col3, col4 = st.columns([2,1,8])

# filters for yards
with col1:
    min_pass_yards = st.number_input('Min Pass Yds', step = 1, min_value = 0, value = 0)
    min_rush_yards = st.number_input('Min Rush Yds', step = 1, min_value = 0, value = 0)
    min_rec_yards = st.number_input('Min Rec Yds', step = 1, min_value = 0, value = 0)
    year = st.number_input('Year', step = 1, min_value = 1947, max_value = 2040, value = None)
    totals = st.checkbox('Show Full Game Totals', value = True)
    simple = st.checkbox('Simple View', value = True)


# max filters
# with col2:
#     max_pass_yards = st.number_input('Maximum Pass Yards', step = 1, min_value = 0, value = None)
#     max_rush_yards = st.number_input('Maximum Rush Yards', step = 1, min_value = 0, value = None)
#     max_rec_yards = st.number_input('Maximum Receiving Yards', step = 1, min_value = 0, value = None)

# filters for TDs
with col3:
    min_pass_TDs = st.number_input('Min Pass TDs', step = 1, min_value = 0, value = 0)
    min_rush_TDs = st.number_input('Min Rush TDs', step = 1, min_value = 0, value = 0)
    min_rec_TDs = st.number_input('Min Rec TDs', step = 1, min_value = 0, value = 0)
    

# column for dataset
with col4:
    filtered_stats = master_stats
   
    filtered_stats = filtered_stats[(filtered_stats['Pass Yards'] >= min_pass_yards) & 
                                    (filtered_stats['Net Rush Yards'] >= min_rush_yards) & 
                                    (filtered_stats['Receiving Yards'] >= min_rec_yards) & 
                                    (filtered_stats['Passing TDs'] >= min_pass_TDs) & 
                                    (filtered_stats['Rushing TDs'] >= min_rush_TDs) & 
                                    (filtered_stats['Receiving TDs'] >= min_rec_TDs)]
    
    if year != None:
        filtered_stats = filtered_stats[filtered_stats['Year'] == str(year)]

    if totals == True:
        filtered_stats = filtered_stats[master_stats['Last Name'] == 'Game']
        filtered_stats.drop('First Name', axis=1, inplace=True)
        filtered_stats.rename(columns={'Last Name': ''}, inplace=True)
        filtered_stats.sort_values(by='Year', inplace=True)
        filtered_stats.set_index([''], inplace=True)

        if simple == True:
            filtered_stats['Cmp-Att'] = filtered_stats.apply(lambda row: '-'.join(str(int(val)) for val in row[['Completions', 'Pass Attempts']] if pd.notna(val)), axis=1)
            filtered_stats = filtered_stats[['Cmp-Att', 'Interceptions', 'Pass Yards', 'Passing TDs', 'Rush Attempts', 'Net Rush Yards', 'Rushing TDs', 'Yards Per Rush', 'Catches', 'Receiving Yards', 'Receiving TDs', 'Date', 'Link']]

    else:
        filtered_stats = filtered_stats[master_stats['Last Name'] != 'Game']
        filtered_stats.sort_values(by='Last Name', inplace=True)
        filtered_stats.set_index(['First Name', 'Last Name'], inplace=True)

        if simple == True:
            filtered_stats['Cmp-Att'] = filtered_stats.apply(lambda row: '-'.join(str(int(val)) for val in row[['Completions', 'Pass Attempts']] if pd.notna(val)), axis=1)
            filtered_stats = filtered_stats[['Cmp-Att', 'Interceptions', 'Pass Yards', 'Passing TDs', 'Rush Attempts', 'Net Rush Yards', 'Rushing TDs', 'Yards Per Rush', 'Catches', 'Receiving Yards', 'Receiving TDs', 'Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Texas Result', 'Link']]

    st.dataframe(filtered_stats)

    st.download_button('Download Full Data (CSV)', data = master_stats.to_csv(index = False), file_name = "texas_fb_history.csv", key = 'download_full')
    st.download_button('Download Filtered Data (CSV)', data = filtered_stats.to_csv(index = False), file_name = "texas_fb_history_filtered.csv", key = 'download_filtered')
