import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title = "UT Football Box Score History",
    page_icon = "🤘",
    layout = "wide",
    # background_color="#bf5700",  
)

master_offense = pd.read_csv('master_stats_final.csv').sort_values(by='Date')
player_stats = master_offense.dropna(subset='First Name')
game_stats = master_offense[master_offense['Last Name'] == 'Game']

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
    col1, col2 = st.columns([2,7])

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

            if sums['Pass Attempts'] > 0:
                if sums['Pass Yards'] == 1:
                    temp1 = "1 Yard"
                else:
                    temp1 = f"{int(sums['Pass Yards'])} Yards"

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
                    temp1 = "1 Rush"
                else:
                    temp1 = f"{int(sums['Rush Attempts'])} Rushes"

                if sums['Net Rush Yards'] == 1:
                    temp2 = "1 Yard"
                else:
                    temp2 = f"{int(sums['Net Rush Yards'])} Yards"

                if sums['Rushing TDs'] == 1:
                    temp3 = "1 TD"
                else:
                    temp3 = f"{int(sums['Rushing TDs'])} TDs"

                perc = round(sums['Net Rush Yards'] / sums['Rush Attempts'], 1)

                st.caption("Rushing")
                st.code(f"{temp1}\n{temp2}\n{perc} YPC\n{temp3}")

            if sums['Catches'] > 0:
                if sums['Catches'] == 1:
                    temp1 = "1 Reception"
                else:
                    temp1 = f"{int(sums['Catches'])} Receptions"

                if sums['Receiving Yards'] == 1:
                    temp2 = "1 Yard"
                else:
                    temp2 = f"{int(sums['Receiving Yards'])} Yards"

                if sums['Receiving TDs'] == 1:
                    temp3 = "1 TD"
                else:
                    temp3 = f"{int(sums['Receiving TDs'])} TDs"

                st.caption('Receiving')
                st.code(f"{temp1}\n{temp2}\n{temp3}")

            st.write('Select games in the chart to filter the table.')
            nrows = st.slider('', min_value=0, max_value=len(temp_df))

        else:
            sums = career_stats(game_stats)

            perc = 100 * round(sums['Completions'] / sums['Pass Attempts'], 2)
            ypc = round(sums['Net Rush Yards'] / sums['Rush Attempts'], 1)
            
            st.caption('Passing')
            st.code(f"{int(sums['Completions'])}/{int(sums['Pass Attempts'])} - {perc:.1f} %\n{int(sums['Pass Yards'])} Yards\n{int(sums['Passing TDs'])} TDs\n{int(sums['Interceptions'])} Ints")
            
            st.caption('Rushing')
            st.code(f"{int(sums['Rush Attempts'])} Rushes\n{int(sums['Net Rush Yards'])} Yards\n{ypc} YPC\n{int(sums['Rushing TDs'])} TDs")

            st.caption('Receiving')
            st.code(f"{int(sums['Catches'])} Receptions\n{int(sums['Receiving Yards'])} Yards\n{int(sums['Receiving TDs'])} TDs")

            st.caption('Note some discrepancies in the data. This is not my fault! Here is a list of games with misinputted data:')
            st.caption('Rice 1948, Alabama 1960, Oregon State 1980, Oklahoma 1980, UNC 1982, TCU 1989, Louisville 1994, Baylor 1994, Nebraska 1996')

    with col2:
        if option == 0:
            st.title('Texas Football Offensive History')

            temp_df = master_offense[master_offense['Last Name'] == 'Game']
            
            interval = alt.selection_interval(encodings=['x'])

            color_scale = alt.Scale(range=['#ebceb7', '#bf5700'])


            chart = alt.Chart(temp_df).mark_bar().encode(
                x = alt.X('Date', 
                          title = '',
                          axis = None),  
                y = alt.Y('Fantasy:Q', 
                          title='Team Fantasy Points'), 
                color = alt.condition(interval, 
                                      'Season', 
                                      alt.value("lightgrey"), 
                                      scale = color_scale,
                                      legend = None),
                tooltip = ['Date', 'Opponent', 'Score']
            ).add_selection(
                interval 
            ).properties(
                width=800,
                height=300
            )
            chart

            st.dataframe(master_offense)
        else:
            st.title(option)
            ## attach games that the player missed
            start = min(temp_df['Season'])
            end = max(temp_df['Season'])

            dates = game_stats[(game_stats['Season'] >= start) &
                               (game_stats['Season'] <= end)].reset_index()

            in_temp_df = dates['Date'].isin(temp_df['Date'])

            for i in range(len(dates)):
                if not in_temp_df[i]:
                    new_row = pd.DataFrame([[i, temp_df['First Name'][0],temp_df['Last Name'][0],0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,dates['GameID'][i],dates['Link'][i],dates['Date'][i],dates['Home Team'][i],dates['Away Team'][i],dates['Home Score'][i],dates['Away Score'][i],dates['Texas Result'][i],dates['Season'][i],dates['Year'][i],temp_df['PlayerID'][0],temp_df['NameConcat'][0],temp_df['First Year'][0],temp_df['Last Year'][0],dates['Opponent'][i],dates['Score'],0.0]], columns=temp_df.columns, index=[0])
                    temp_df = pd.concat([new_row, temp_df], ignore_index=True)

            ## make bar chart
            brush = alt.selection_interval(encodings=['x'])

            color_scale = alt.Scale(range=['#ebceb7', '#bf5700'])

            chart_selection = alt.Chart(temp_df).mark_bar().encode(
                x = alt.X('Date', 
                          title = '',
                          axis = None),  
                y = alt.Y('Fantasy:Q', 
                          title='Fantasy Points'), 
                color = alt.condition(brush, 
                                      'Season', 
                                      alt.value("lightgrey"), 
                                      scale = color_scale,
                                      legend = None),
                tooltip = ['Opponent', 'Score']
            ).add_selection(
                brush 
            ).properties(
                width=800,
                height=300
            )

            chart_base = alt.Chart(temp_df).mark_bar().encode(
                x = alt.X('Date', 
                          title = '',
                          axis = None),  
                y = alt.Y('Fantasy:Q', 
                          title='Fantasy Points'), 
                color = alt.condition(brush, 
                                      'Season', 
                                      alt.value("lightgrey"), 
                                      scale = color_scale,
                                      legend = None),
                tooltip = ['Opponent', 'Score']
            ).transform_filter(
                brush 
            ).properties(
                width=800,
                height=300
            )

            ranked_text = alt.Chart(temp_df).mark_text(align='right').encode(
                y=alt.Y('row_number:O',axis=None),
                color = alt.value('white')
            ).transform_filter(
                brush
            ).transform_window(
                row_number='row_number()'
            ).properties(
                width=1
            ).transform_filter('datum.row_number < 10')

            # Data Tables
            date = ranked_text.encode(text='Date:T').properties(title=alt.TitleParams(text='Date', align='right'))
            opp = ranked_text.encode(text='Opponent:N').properties(title=alt.TitleParams(text='Opponent', align='right'))

            passyds = ranked_text.encode(text='Pass Yards:Q').properties(title=alt.TitleParams(text='Pass Yards', align='right'))
            passtds = ranked_text.encode(text='Passing TDs:Q').properties(title=alt.TitleParams(text='Passing TDs', align='right'))
            
            rushyds = ranked_text.encode(text='Net Rush Yards:Q').properties(title=alt.TitleParams(text='Rush Yards', align='right'))
            rushtds = ranked_text.encode(text='Rushing TDs:Q').properties(title=alt.TitleParams(text='Rush TDs', align='right'))

            recyds = ranked_text.encode(text='Receiving Yards:Q').properties(title=alt.TitleParams(text='Receiving Yards', align='right'))
            rectds = ranked_text.encode(text='Receiving TDs:Q').properties(title=alt.TitleParams(text='Receiving TDs', align='right'))
            
            text = alt.hconcat(date, opp, passyds, passtds, rushyds, rushtds, recyds, rectds) # Combine data tables

            # Build chart
            x = alt.vconcat(
                chart_base + chart_selection,
                text
            ).resolve_legend(
                color="independent"
            ).configure_view(strokeWidth=0)
            
            x
            


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