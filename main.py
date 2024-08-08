import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title = "UT Football Box Score History",
    page_icon = "🤘",
    layout = "wide",
    initial_sidebar_state="expanded",
)

master_offense = pd.read_csv('offensive_stats_final.csv').sort_values(by='Date')
master_defense = pd.read_csv('defensive_stats_final.csv').sort_values(by='Date')

player_stats = master_offense.dropna(subset='First Name')
game_stats = master_offense[master_offense['Last Name'] == 'Game']

player_stats_def = master_defense.dropna(subset='First Name')
game_stats_def = master_defense[master_defense['Last Name'] == 'Game']

career_stats_off = pd.read_csv('offensive_career_stats.csv')
career_stats_def = pd.read_csv('defensive_career_stats.csv')

all_passers = career_stats_off[career_stats_off['Pass Yards'] != 0]['Pass Yards']
all_rushers = career_stats_off[career_stats_off['Net Rush Yards'] != 0]['Net Rush Yards']
all_receivers = career_stats_off[career_stats_off['Receiving Yards'] != 0]['Receiving Yards']

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
    

def offense():
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

            start = min(temp_df['Season'])
            end = max(temp_df['Season'])

            dates = game_stats[(game_stats['Season'] >= start) &
                               (game_stats['Season'] <= end)].reset_index()

            st.caption('Different colors in the chart correspond to different seasons. For more information, hover over the chart or refer to the game log.')
            st.caption('Download the game log to open the csv in Excel.')
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

            st.caption('Note some discrepancies in the receiving/passing stats. This is not my fault! Here is a list of games with misinputted data:')
            st.caption('Rice 1948, Alabama 1960, Oregon State 1980, Oklahoma 1980, UNC 1982, TCU 1989, Louisville 1994, Baylor 1994, Nebraska 1996')
            st.caption('Download the game log to see all available columns.')
    with col2:
        if option == 0:
            st.title('Texas Football Offensive History')

            temp_df = master_offense[master_offense['Last Name'] == 'Game']

            # cumulative wins
            temp_df['result'] = temp_df['Texas Result'].apply(lambda x: 1 if x == 'Win' else (-1 if x == 'Loss' else 0))
            temp_df['win_diff'] = temp_df['result'].cumsum()

            color_scale = alt.Scale(range=['#ebceb7', '#bf5700'])
            color_scale_res = alt.Scale(domain=['Loss', 'Tie',  'Win'], range=['#ebceb7', '#bf5700', '#7fbf7f', '#2c7bb6'])


            brush = alt.selection_interval(encodings=['x'])

            header = alt.Chart(temp_df).mark_bar().encode(
                x = alt.X('Date', 
                          title = '',
                          axis = None),  
                y = alt.Y('Team Fantasy:Q', 
                          title=''),
                color=alt.condition(
                    alt.datum['Texas Result'] == 'Win',
                    alt.value('#bf5700'),
                    alt.value('#ebceb7')), 
                tooltip = ['Date', 'Opponent', 'Score']
            ).add_params(
                brush
            )

            chart = alt.Chart(temp_df).mark_bar().encode(
                x = alt.X('Date', 
                          title = '',
                          axis = None),  
                y = alt.Y('win_diff:Q', 
                          title='Win Differential (since 1947)'), 
                color = alt.Color('Season', 
                                 scale=color_scale,
                                 legend=None),
                tooltip = ['Date', 'Opponent', 'Score']
            )
            # .transform_filter(
            #     brush
            # )
            
            x = alt.vconcat(
                header, chart)

            ### note to future sam: I commented out the original stacked chart
            st.altair_chart(chart, use_container_width=True)

            # full stats
            dl_df = temp_df[['Date','Opponent','Score','Completions','Pass Attempts','Interceptions','Pass Yards','Passing TDs','Longest Pass','Sacks Taken','Rush Attempts','Rush Yards Gained','Rush Yards Lost','Net Rush Yards','Rushing TDs','Longest Rush','Yards Per Rush','Catches','Receiving Yards','Receiving TDs','Longest Reception','Total Yards','Total TDs','Season','Link']]

            temp_df['Cmp/Att'] = temp_df['Completions'].astype(int).astype(str) + '/' + temp_df['Pass Attempts'].astype(int).astype(str)

            # un expanded stats
            temp_df = temp_df[['Cmp/Att','Pass Yards','Passing TDs','Interceptions','Rush Attempts','Net Rush Yards','Rushing TDs','Catches','Receiving Yards','Receiving TDs','Date','Opponent','Score','Link']]

            temp_df.rename(columns = {'Pass Yards': 'Pass Yds',
                                      'Passing TDs': 'Pass TDs',
                                      'Interceptions': 'Int',
                                      'Rush Attempts': 'Rush',
                                      'Net Rush Yards': 'Rush Yds',
                                      'Rushing TDs': 'Rush TDs',
                                      'Catches': 'Rec',
                                      'Receiving Yards': 'Rec Yds',
                                      'Receiving TDs': 'Rec TDs'},
                           inplace = True)
            
            temp_df.sort_values(by = 'Date')
            temp_df.set_index(['Date', 'Opponent', 'Score'], inplace = True)

            st.header('Full Game History')
            st.dataframe(temp_df)
        
            st.download_button(label = 'Download Game Log', data = dl_df.to_csv(index = True), file_name = 'full_gamelog.csv')
        else:
            st.title(option)

            # clone for blurb section
            clone_df = temp_df

            ## attach games that the player missed
            in_temp_df = dates['Date'].isin(temp_df['Date'])

            for i in range(len(dates)):
                if not in_temp_df[i]:
                    new_row = pd.DataFrame([[i, temp_df['First Name'][0],temp_df['Last Name'][0],0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,dates['GameID'][i],dates['Link'][i],dates['Date'][i],dates['Home Team'][i],dates['Away Team'][i],dates['Home Score'][i],dates['Away Score'][i],dates['Texas Result'][i],dates['Season'][i],0.0,0.0,dates['Year'][i],temp_df['PlayerID'][0],temp_df['NameConcat'][0],temp_df['First Year'][0],temp_df['Last Year'][0],dates['Opponent'][i],dates['Score'][i],0.0,0.0]], columns=temp_df.columns, index=[0])
                    temp_df = pd.concat([new_row, temp_df], ignore_index=True)

            temp_df = temp_df.sort_values(by = 'Date')

            
            ## make bar chart
            # brush = alt.selection_interval(encodings=['x'])

            color_scale = alt.Scale(range=['#ebceb7', '#bf5700'])

            zero_ind = max(temp_df['Total Yards']) * 0.005

            base_chart = alt.Chart(temp_df).transform_calculate(
                Total_Yards_Offset=f'datum["Total Yards"] == 0 ? {zero_ind} : datum["Total Yards"]'
            ).mark_bar().encode(
                x=alt.X('Date', title='', axis=None),
                y=alt.Y('Total_Yards_Offset:Q', title='Total Yards'),
                color=alt.Color('Season', scale=color_scale, legend=None),
                tooltip=['Opponent', 'Date', 'Total Yards', 'Total TDs', 'Score']
            )
            
            st.altair_chart(base_chart, use_container_width=True)

            col2_1_1, col2_2_2 = st.columns([1,1])

            with col2_1_1:

                small_df = temp_df[['First Name', 'Last Name', 'Date', 'Opponent', 'Score', 'Pass Yards', 'Net Rush Yards', 'Receiving Yards', 'Season', 'Total Yards']]                
                season_stats = small_df.groupby(['Season']).sum().reset_index()
                season_stats['Season'].astype(int).astype(str)

                chart = alt.Chart(season_stats).mark_bar(size = 15).encode(
                    x=alt.X('Total Yards:Q', title='Total Yards'),
                    y=alt.Y('Season:O', title='Season'),
                    color=alt.Color('Season', scale=color_scale, legend=None),
                    tooltip=['Season', 'Pass Yards', 'Net Rush Yards', 'Receiving Yards']
                )

                st.altair_chart(chart, use_container_width=True)
            
            with col2_2_2:
                win = len(clone_df[clone_df['Texas Result'] == 'Win'])
                loss = len(clone_df[clone_df['Texas Result'] == 'Loss'])
                tie = len(clone_df[clone_df['Texas Result'] == 'Tie'])

                tot_pass = temp_df['Pass Yards'].sum()
                tot_rush = temp_df['Net Rush Yards'].sum()
                tot_rec = temp_df['Receiving Yards'].sum()

                pass_bool = False
                rush_bool = False
                rec_bool = False

                if tot_pass > tot_rush and tot_pass > tot_rec:
                    pass_bool = True
                elif tot_rec > tot_rush and tot_rec > tot_pass:
                    rec_bool = True
                else:
                    rush_bool = True

                if tot_pass > 1000:
                    pass_bool = True
                if tot_rec > 500:
                    rec_bool = True
                if tot_rush > 500:
                    rush_bool = True
                
                sent_list = ['', '', '']
                desc_list = ['passing', 'rushing', 'receiving']
                bool_list = [pass_bool, rush_bool, rec_bool]
                career_list = [all_passers, all_rushers, all_receivers]
                tot_list = [tot_pass, tot_rush, tot_rec]

                for i in range(3):
                    if bool_list[i]:
                        perc = (career_list[i] < tot_list[i]).mean() * 100
                        sent_list[i] = f"He is in the {perc:.0f}th percentile in {desc_list[i]} yards."

                st.caption(f"{clone_df['First Name'][0]} {clone_df['Last Name'][0]} has a record of {win}-{loss}-{tie} in games in which he recorded a stat while at Texas. {sent_list[0]} {sent_list[1]} {sent_list[2]}")

            st.subheader('Game Log')

            col2_1, col2_2 = st.columns([6,1])

            with col2_2:
                st.caption('Season')

                season_dict = {}
                seasons = temp_df['Season'].unique()

                for season in seasons:
                    season_dict[season] = st.checkbox(str(season), value=True)

                selected_seasons = [season for season, selected in season_dict.items() if selected]

                st.caption('Type')
                
                show_pass = st.checkbox('Passing', value = pass_bool)
                show_rush = st.checkbox('Rushing', value = rush_bool)
                show_rec = st.checkbox('Receiving', value = rec_bool)

                temp_df['Cmp/Att'] = temp_df['Completions'].astype(int).astype(str) + '/' + temp_df['Pass Attempts'].astype(int).astype(str)

                pass_col = ['Cmp/Att','Pass Yards','Passing TDs','Interceptions']
                rush_col = ['Rush Attempts','Net Rush Yards','Rushing TDs']
                rec_col = ['Catches','Receiving Yards','Receiving TDs']
                cols = [pass_col, rush_col, rec_col]
                misc_col = ['Date','Opponent','Score','Link']

                col_list = []
                full_col_list = []
                col_bools = [show_pass, show_rush, show_rec]
                for i in range(3):
                    full_col_list.extend(cols[i])
                    if col_bools[i]:
                        col_list.extend(cols[i])
                
                col_list.extend(misc_col)
                full_col_list.extend(misc_col)

            with col2_1:
                dl_log = temp_df[full_col_list]
                
                game_log = temp_df[temp_df['Season'].isin(selected_seasons)]
                game_log = game_log[col_list]

                game_log.set_index(['Date', 'Opponent', 'Score'], inplace = True)
                dl_log.set_index(['Date', 'Opponent', 'Score'], inplace = True)

                game_log.rename(columns = {'Pass Yards': 'Pass Yds',
                                           'Passing TDs': 'Pass TDs',
                                           'Interceptions': 'Int',
                                           'Rush Attempts': 'Rush',
                                           'Net Rush Yards': 'Rush Yds',
                                           'Rushing TDs': 'Rush TDs',
                                           'Catches': 'Rec',
                                           'Receiving Yards': 'Rec Yds',
                                           'Receiving TDs': 'Rec TDs'},
                           inplace = True)
                
                dl_log.rename(columns = {'Pass Yards': 'Pass Yds',
                                         'Passing TDs': 'Pass TDs',
                                         'Interceptions': 'Int',
                                         'Rush Attempts': 'Rush',
                                         'Net Rush Yards': 'Rush Yds',
                                         'Rushing TDs': 'Rush TDs',
                                         'Catches': 'Rec',
                                         'Receiving Yards': 'Rec Yds',
                                         'Receiving TDs': 'Rec TDs'},
                           inplace = True)

                st.dataframe(game_log)

                st.download_button('Download Filtered Game Log', game_log.to_csv(index = True), file_name = f"{temp_df['Last Name'][0]}_{temp_df['First Name'][0]}_filtered_game_log.csv")
                st.download_button('Download Full Game Log', dl_log.to_csv(index = True), file_name = f"{temp_df['Last Name'][0]}_{temp_df['First Name'][0]}_full_game_log.csv")

            # # text labels
            # text = base_chart.mark_text(
            #     align = 'center',
            #     baseline = 'middle',
            #     dx = 30,
            #     dy = -20,
            #     angle = 305 
            # ).encode(
            #     text = alt.Text('Opponent:N'),
            #     color = alt.value('white')
            # )

            # # Chart with selection
            # chart_selection = base_chart.add_params(
            #     brush
            # ).properties(
            #     width=800,
            #     height=300
            # )

            # # Chart base with filter
            # chart_base = base_chart.transform_filter(
            #     brush
            # ).properties(
            #     width=800,
            #     height=300
            # )

            # # filterable table
            # nrows = len(dates)
            # row_limit = str(f'datum.row_number < {nrows}')

            # ranked_text = alt.Chart(temp_df).mark_text(align='right').encode(
            #     y=alt.Y('row_number:O', axis=None),
            #     text=alt.Text('value:Q'),  # Added to display some text
            #     color=alt.value('white')
            # ).transform_filter(
            #     brush
            # ).transform_window(
            #     row_number='row_number()'
            # ).properties(
            #     width=1,
            #     height=nrows*16
            # ).transform_filter(
            #     row_limit
            # )

            # # Data Tables
            # date = ranked_text.encode(text='Date:T').properties(title=alt.TitleParams(text='Date', align='right'))
            # opp = ranked_text.encode(text='Opponent:N').properties(title=alt.TitleParams(text='Opponent', align='right'))

            # passyds = ranked_text.encode(text='Pass Yards:Q').properties(title=alt.TitleParams(text='Pass Yards', align='right'))
            # passtds = ranked_text.encode(text='Passing TDs:Q').properties(title=alt.TitleParams(text='Passing TDs', align='right'))
            # 
            # rushyds = ranked_text.encode(text='Net Rush Yards:Q').properties(title=alt.TitleParams(text='Rush Yards', align='right'))
            # rushtds = ranked_text.encode(text='Rushing TDs:Q').properties(title=alt.TitleParams(text='Rush TDs', align='right'))

            # recyds = ranked_text.encode(text='Receiving Yards:Q').properties(title=alt.TitleParams(text='Receiving Yards', align='right'))
            # rectds = ranked_text.encode(text='Receiving TDs:Q').properties(title=alt.TitleParams(text='Receiving TDs', align='right'))
            # 
            # text = alt.hconcat(date, opp, passyds, passtds, rushyds, rushtds, recyds, rectds) # Combine data tables

            #  # Build chart
            #  x = alt.vconcat(
            #      chart_ base + chart_selection,
            #      text
            #  ).resolve_legend(
            #      color="independent"
            #  ).configure_view(strokeWidth=0)

def home():
    st.title('Texas Football Box Score Project')

    col_1, col_2, col_3 = st.columns([5,1,5])

    with col_1:
        st.text('')
        st.markdown("**Hello! My name is Sam Queralt.** Texas football's stats are all digitized, but not easily accessible. They're all in different places, and they can't be searched or filtered. I'm not great at coding, but I know enough about web scraping to put together a database of all the Texas box scores I have access to. This is not affiliated with UT, and there are surely errors littered throughout the database. Please contact @sam_queralt on Twitter if you find anything that needs fixing. Also tag me if you use this tool to find a stat! I'm curious what quirks there are to find (see the Bowmer mystery). Happy searching!")

    with col_3:
        st.text('')
        st.text('')
        st.text('')
        st.subheader('Quick Download')

        # master_defense.rename(columns={'##',Last Name,First Name,Solo,Ast,Tot,TFL,tfl_yds,FF,FR,fr_yd,Int,int_yds,BrUp,Blkd,Sack,sack_yds,QH,GameID,Date,Home Team,Away Team,Home Score,Away Score,Texas Result,Link,Season,fr_yds,Year,PlayerID,NameConcat,First Year,Last Year,Opponent,Score},
        #     inplace=True)


        # st.download_button("")

def defense(): 
    st.title("Coming soon.")

def records():
    st.title("Coming soon.")
    ## find games in a row

def bowmer():
    st.title("Bowmer")
    # also include other finds like the high sack game or the onlyfans links

# Dictionary of pages
PAGES = {
    "Home": home,
    "Offense": offense,
    "Defense": defense,
    "Record Search": records,
    "Database": main,
    "The Bowmer Mystery": bowmer
}


st.sidebar.title('Navigation')
st.sidebar.caption("Select a page to navigate to below. Close this navigation bar once you've chosen a page for optimized viewing.")

selection = st.sidebar.radio("", list(PAGES.keys()))

st.sidebar.caption("Please report any errors to @sam_queralt on Twitter.")

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