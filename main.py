import streamlit as st
import pandas as pd
st.set_page_config(
    page_title = "UT Football Box Score History",
    page_icon = "🤘",
    layout = "wide",
    # background_color="#bf5700",  
)

master_offense = pd.read_csv('master_stats_final.csv')
player_stats = master_offense.dropna(subset='First Name')

keys = []
for index, row in player_stats.iterrows():
    first_year = int(row['First Year'])
    last_year = int(row['Last Year'])
    key = f"{row['First Name']} {row['Last Name']}, {first_year}-{last_year}"
    keys.append(key)

values = list(player_stats['PlayerID'])
name_dict = dict(map(lambda i,j : (i,j) , keys,values))


# Function to filter the list based on the search query
def filter_list(query, data):
    if query:
        return [item for item in data if query.lower() in item.lower()]
    else:
        return data

def career_stats(df):
    numeric_sums = df.select_dtypes(include='number').sum(axis=0)
    return numeric_sums

# Define the page functions
def main():
    st.title("UT Football Box Score History", anchor = None)

    master_stats = pd.read_csv("master_stats_final.csv")
    master_stats[['Year', 'Month', 'Day']] = master_stats['Date'].str.split('-', expand=True)

    # simple col names
    simple_mapping = {'First Name': 'First',
                      'Last Name': 'Last',
                      'Interceptions': 'Int',
                      'Pass Yards': 'Pass Yds',
                      'Passing TDs': 'Pass TDs',
                      'Rush Attempts': 'Rsh',
                      'Net Rush Yards': 'Rush Yds',
                      'Yards Per Rush': 'YPR',
                      'Catches': 'Rec',
                      'Receiving Yards': 'Rec Yds',
                      'Receiving TDs': 'Rec TDs',
                      'Home Team': 'Home', 
                      'Away Team': 'Away'}

    name_mapping = {'First Name': 'First',
                    'Last Name': 'Last'}

    # Colunms
    col1, col3, col4 = st.columns([2,1,8])

    # filters for yards
    with col1:
        last_name = st.text_input("Last")
        min_pass_yards = st.number_input('Min Pass Yds', step = 1, min_value = 0, value = None)
        min_rush_yards = st.number_input('Min Rush Yds', step = 1, min_value = 0, value = None)
        min_rec_yards = st.number_input('Min Rec Yds', step = 1, min_value = 0, value = None)
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
        first_name = st.text_input("First")
        min_pass_TDs = st.number_input('Min Pass TDs', step = 1, min_value = 0, value = 0)
        min_rush_TDs = st.number_input('Min Rush TDs', step = 1, min_value = 0, value = 0)
        min_rec_TDs = st.number_input('Min Rec TDs', step = 1, min_value = 0, value = 0)

    # column for dataset
    with col4:
        filtered_stats = master_stats

        if min_pass_yards != None:
            filtered_stats = filtered_stats[filtered_stats['Pass Yards'] >= min_pass_yards]
        if min_rush_yards != None:
            filtered_stats = filtered_stats[filtered_stats['Net Rush Yards'] >= min_rush_yards]
        if min_rec_yards != None:
            filtered_stats = filtered_stats[filtered_stats['Receiving Yards'] >= min_rec_yards]

        filtered_stats = filtered_stats[(filtered_stats['Passing TDs'] >= min_pass_TDs) & 
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
                filtered_stats['Cmp/Att'] = filtered_stats.apply(lambda row: '/'.join(str(int(val)) for val in row[['Completions', 'Pass Attempts']] if pd.notna(val)), axis=1)
                filtered_stats = filtered_stats[['Cmp/Att', 'Interceptions', 'Pass Yards', 'Passing TDs', 'Rush Attempts', 'Net Rush Yards', 'Rushing TDs', 'Yards Per Rush', 'Catches', 'Receiving Yards', 'Receiving TDs', 'Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Texas Result', 'Link']]
                filtered_stats.rename(columns = simple_mapping, inplace = True)

        else:
            filtered_stats = filtered_stats[master_stats['Last Name'] != 'Game']
            filtered_stats.sort_values(by='Last Name', inplace=True)
            filtered_stats = filtered_stats[filtered_stats['First Name'].str.contains(first_name, na = False)]
            filtered_stats = filtered_stats[filtered_stats['Last Name'].str.contains(last_name, na = False)]
    #        filtered_stats.rename(columns = name_mapping, inplace = True)
            filtered_stats.set_index(['First Name', 'Last Name'], inplace=True)

            if simple == True:
                filtered_stats['Cmp/Att'] = filtered_stats.apply(lambda row: '/'.join(str(int(val)) for val in row[['Completions', 'Pass Attempts']] if pd.notna(val)), axis=1)
                filtered_stats = filtered_stats[['Cmp/Att', 'Interceptions', 'Pass Yards', 'Passing TDs', 'Rush Attempts', 'Net Rush Yards', 'Rushing TDs', 'Yards Per Rush', 'Catches', 'Receiving Yards', 'Receiving TDs', 'Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Texas Result', 'Link']]
                filtered_stats.rename(columns = simple_mapping, inplace = True)

        st.dataframe(filtered_stats)

        st.download_button('Download Full Data (CSV)', data = master_stats.to_csv(index = False), file_name = "texas_fb_history.csv", key = 'download_full')
        st.download_button('Download Filtered Data (CSV)', data = filtered_stats.to_csv(index = False), file_name = "texas_fb_history_filtered.csv", key = 'download_filtered')

    st.text('Note: Some players names have typos in the official stat sheets and may not show up in name based queries.')
    st.text('Also, stats have not been rigorously validated, so this is an UNOFFICIAL data set.')
    st.text('All the stats here should be accurate, but I could be missing some games it\'s hard to be 100% sure')
    st.text('Stats will not be updated until the most recent season is posted at this link: https://texassports.com/sports/2013/7/21/FB_0721134841.aspx')
    st.text('Defensive stats are on the way. Prepare for some weird names because the early box score pages cut them off for spacing reasons.')
    

def search():    
    col1, col2 = st.columns([2,6])

    with col1:
        option = st.selectbox(
                    "",
                    name_dict,
                    index=None,
                    placeholder="Search for player...",
                    )
        if option:
            pass
        else:
            option = 0

        if option != 0:
            temp_df = master_offense[master_offense['PlayerID'] == name_dict[option]].reset_index()
            sums = career_stats(temp_df)

            st.write('Career Stats:')

            if sums['Pass Attempts'] > 0:
                if sums['Pass Yards'] == 1:
                    temp1 = "1 yard"
                else:
                    temp1 = f"{int(sums['Pass Yards'])} yards"

                if sums['Passing TDs'] == 1:
                    temp2 = "1 TD"
                else:
                    temp2 = f"{int(sums['Passing TDs'])} TDs"
                
                if sums['Interceptions'] == 1:
                    temp3 = "1 Int"
                else:
                    temp3 = f"{int(sums['Interceptions'])} Ints"

                perc = 100 * round(sums['Completions'] / sums['Pass Attempts'], 2)

                st.caption("Passing")
                st.code(f"{int(sums['Completions'])}/{int(sums['Pass Attempts'])} - {perc:.1f} %\n{temp1}\n{temp2}\n{temp3}")
            
            if sums['Rush Attempts'] > 0:
                if sums['Rush Attempts'] == 1:
                    temp1 = "1 rush"
                else:
                    temp1 = f"{int(sums['Rush Attempts'])} rushes"

                if sums['Net Rush Yards'] == 1:
                    temp2 = "1 yard"
                else:
                    temp2 = f"{int(sums['Net Rush Yards'])} yards"

                if sums['Rushing TDs'] == 1:
                    temp3 = "1 TD"
                else:
                    temp3 = f"{int(sums['Rushing TDs'])} TDs"

                perc = round(sums['Net Rush Yards'] / sums['Rush Attempts'], 1)

                st.caption("Rushing")
                st.code(f"{temp1}\n{temp2}\n{perc} YPC\n{temp3}")

            if sums['Catches'] > 0:
                if sums['Catches'] == 1:
                    temp1 = "1 reception"
                else:
                    temp1 = f"{int(sums['Catches'])} receptions"

                if sums['Receiving Yards'] == 1:
                    temp2 = "1 yard"
                else:
                    temp2 = f"{int(sums['Receiving Yards'])} yards"

                if sums['Receiving TDs'] == 1:
                    temp3 = "1 TD"
                else:
                    temp3 = f"{int(sums['Receiving TDs'])} TDs"

                st.caption('Receiving')
                st.code(f"{temp1}\n{temp2}\n{temp3}")
            else:
                # for full texas history
                pass

    with col2:
        if option == 0:
            st.title('Texas Football History')
        else:
            pass
            # st.dataframe(temp_df)
            # st.dataframe(sums)


# Dictionary of pages
PAGES = {
    "Main": main,
    "Search": search,
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]
page()



##  def main():
##      st.title("Main Page")
##      st.write("Welcome to the main page!")
##      if st.button('Go to Page 1'):
##          st.session_state.page = 'Page 1'
##          st.experimental_rerun()
##      if st.button('Go to Page 2'):
##          st.session_state.page = 'Page 2'
##          st.experimental_rerun()
##  
##  def page1():
##      st.title("Page 1")
##      st.write("Welcome to page 1!")
##      if st.button('Go to Main Page'):
##          st.session_state.page = 'Main'
##          st.experimental_rerun()
##      if st.button('Go to Page 2'):
##          st.session_state.page = 'Page 2'
##          st.experimental_rerun()
##  
##  def page2():
##      st.title("Page 2")
##      st.write("Welcome to page 2!")
##      if st.button('Go to Main Page'):
##          st.session_state.page = 'Main'
##          st.experimental_rerun()
##      if st.button('Go to Page 1'):
##          st.session_state.page = 'Page 1'
##          st.experimental_rerun()
##  
##  # Ensure session state has the 'page' variable
##  if 'page' not in st.session_state:
##      st.session_state.page = 'Main'
##  
##  # Dictionary of pages
##  PAGES = {
##      "Main": main,
##      "Page 1": page1,
##      "Page 2": page2
##  }
##  
##  # Get the function for the current page
##  page = PAGES.get(st.session_state.page, main)
##  
##  # Run the current page function
##  page()



###  # main file for website
###  
###  # to test: streamlit run c:/Code/ut_football_history/main.py
###  # Import convention
###  import streamlit as st
###  import pandas as pd
###  st.set_page_config(
###      page_title = "UT Football Box Score History",
###      page_icon = "🤘",
###      layout = "wide",
###      # background_color="#bf5700",  
###  )
###  
###  
###  st.title("UT Football Box Score History", anchor = None)
###  
###  master_stats = pd.read_csv("master_stats_final.csv")
###  master_stats[['Year', 'Month', 'Day']] = master_stats['Date'].str.split('-', expand=True)
###  
###  # simple col names
###  simple_mapping = {'First Name': 'First',
###                    'Last Name': 'Last',
###                    'Interceptions': 'Int',
###                    'Pass Yards': 'Pass Yds',
###                    'Passing TDs': 'Pass TDs',
###                    'Rush Attempts': 'Rsh',
###                    'Net Rush Yards': 'Rush Yds',
###                    'Yards Per Rush': 'YPR',
###                    'Catches': 'Rec',
###                    'Receiving Yards': 'Rec Yds',
###                    'Receiving TDs': 'Rec TDs',
###                    'Home Team': 'Home', 
###                    'Away Team': 'Away'}
###  
###  name_mapping = {'First Name': 'First',
###                  'Last Name': 'Last'}
###  
###  # Colunms
###  col1, col3, col4 = st.columns([2,1,8])
###  
###  # filters for yards
###  with col1:
###      last_name = st.text_input("Last")
###      min_pass_yards = st.number_input('Min Pass Yds', step = 1, min_value = 0, value = None)
###      min_rush_yards = st.number_input('Min Rush Yds', step = 1, min_value = 0, value = None)
###      min_rec_yards = st.number_input('Min Rec Yds', step = 1, min_value = 0, value = None)
###      year = st.number_input('Year', step = 1, min_value = 1947, max_value = 2040, value = None)
###      totals = st.checkbox('Show Full Game Totals', value = True)
###      simple = st.checkbox('Simple View', value = True)
###  
###  
###  # max filters
###  # with col2:
###  #     max_pass_yards = st.number_input('Maximum Pass Yards', step = 1, min_value = 0, value = None)
###  #     max_rush_yards = st.number_input('Maximum Rush Yards', step = 1, min_value = 0, value = None)
###  #     max_rec_yards = st.number_input('Maximum Receiving Yards', step = 1, min_value = 0, value = None)
###  
###  # filters for TDs
###  with col3:
###      first_name = st.text_input("First")
###      min_pass_TDs = st.number_input('Min Pass TDs', step = 1, min_value = 0, value = 0)
###      min_rush_TDs = st.number_input('Min Rush TDs', step = 1, min_value = 0, value = 0)
###      min_rec_TDs = st.number_input('Min Rec TDs', step = 1, min_value = 0, value = 0)
###      
###  # column for dataset
###  with col4:
###      filtered_stats = master_stats
###      
###      if min_pass_yards != None:
###          filtered_stats = filtered_stats[filtered_stats['Pass Yards'] >= min_pass_yards]
###      if min_rush_yards != None:
###          filtered_stats = filtered_stats[filtered_stats['Net Rush Yards'] >= min_rush_yards]
###      if min_rec_yards != None:
###          filtered_stats = filtered_stats[filtered_stats['Receiving Yards'] >= min_rec_yards]
###      
###      filtered_stats = filtered_stats[(filtered_stats['Passing TDs'] >= min_pass_TDs) & 
###                                      (filtered_stats['Rushing TDs'] >= min_rush_TDs) & 
###                                      (filtered_stats['Receiving TDs'] >= min_rec_TDs)]
###  
###      if year != None:
###          filtered_stats = filtered_stats[filtered_stats['Year'] == str(year)]
###  
###      if totals == True:
###          filtered_stats = filtered_stats[master_stats['Last Name'] == 'Game']
###          filtered_stats.drop('First Name', axis=1, inplace=True)
###          filtered_stats.rename(columns={'Last Name': ''}, inplace=True)
###          filtered_stats.sort_values(by='Year', inplace=True)
###          filtered_stats.set_index([''], inplace=True)
###  
###          if simple == True:
###              filtered_stats['Cmp/Att'] = filtered_stats.apply(lambda row: '/'.join(str(int(val)) for val in row[['Completions', 'Pass Attempts']] if pd.notna(val)), axis=1)
###              filtered_stats = filtered_stats[['Cmp/Att', 'Interceptions', 'Pass Yards', 'Passing TDs', 'Rush Attempts', 'Net Rush Yards', 'Rushing TDs', 'Yards Per Rush', 'Catches', 'Receiving Yards', 'Receiving TDs', 'Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Texas Result', 'Link']]
###              filtered_stats.rename(columns = simple_mapping, inplace = True)
###  
###      else:
###          filtered_stats = filtered_stats[master_stats['Last Name'] != 'Game']
###          filtered_stats.sort_values(by='Last Name', inplace=True)
###          filtered_stats = filtered_stats[filtered_stats['First Name'].str.contains(first_name, na = False)]
###          filtered_stats = filtered_stats[filtered_stats['Last Name'].str.contains(last_name, na = False)]
###  #        filtered_stats.rename(columns = name_mapping, inplace = True)
###          filtered_stats.set_index(['First Name', 'Last Name'], inplace=True)
###  
###          if simple == True:
###              filtered_stats['Cmp/Att'] = filtered_stats.apply(lambda row: '/'.join(str(int(val)) for val in row[['Completions', 'Pass Attempts']] if pd.notna(val)), axis=1)
###              filtered_stats = filtered_stats[['Cmp/Att', 'Interceptions', 'Pass Yards', 'Passing TDs', 'Rush Attempts', 'Net Rush Yards', 'Rushing TDs', 'Yards Per Rush', 'Catches', 'Receiving Yards', 'Receiving TDs', 'Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Texas Result', 'Link']]
###              filtered_stats.rename(columns = simple_mapping, inplace = True)
###  
###      st.dataframe(filtered_stats)
###  
###      st.download_button('Download Full Data (CSV)', data = master_stats.to_csv(index = False), file_name = "texas_fb_history.csv", key = 'download_full')
###      st.download_button('Download Filtered Data (CSV)', data = filtered_stats.to_csv(index = False), file_name = "texas_fb_history_filtered.csv", key = 'download_filtered')
###  
###  st.text('Note: Some players names have typos in the official stat sheets and may not show up in name based queries.')
###  st.text('Also, stats have not been rigorously validated, so this is an UNOFFICIAL data set.')
###  st.text('All the stats here should be accurate, but I could be missing some games it\'s hard to be 100% sure')
###  st.text('Stats will not be updated until the most recent season is posted at this link: https://texassports.com/sports/2013/7/21/FB_0721134841.aspx')
###  st.text('Defensive stats are on the way. Prepare for some weird names because the early box score pages cut them off for spacing reasons.')
###  
###  # notes on defense
###  ### early names cut off due to spacing
###  ### some years count assisted tackles as .5 while some count them at 1