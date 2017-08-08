from bs4 import BeautifulSoup
from bs4 import Comment

import requests

import re
import pprint
import json
import datetime
import os


base_mlb = "http://www.espn.com"
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#               Could generalise this to the team data. The format works the same...

def ScrapeStatsDataTableRows(table_rows):
    all_table_data = {}

    '''
    You are making a 3 tiered dictionary
    depth 0 = each table
    depth 1 = the rows of the table
    depth 2 = the columns of the tables
    values of depth 2 = the cell data...

    '''

    cur_section_key = ""
    header_keys = []

    for row in table_rows:

        row_class = row.get("class")[0]

        if row_class == "colhead":  # Store the keys for each data cell (i.e. columns of header)

            section_header = row.findAll("td")
            cur_section_key = section_header[0].text    # Key for the depth 1 dictionary
            all_table_data[cur_section_key] = {}        # The depth 0 dict (whole table)

            for header_cell in enumerate(section_header):
                if len(header_cell) > 0:
                    header_cell = [x for x in header_cell if "bs4" in str(type(x))][0]  # strip out non bs4 glitches
                header_keys.append(header_cell.text)

        elif row_class == "stathead":
            # USEFUL: The text of the first cell contains the table name!!!
            continue
        else:
            section_data = row.findAll("td")

            for i, cell in enumerate(section_data):
                if i == 0:
                    all_table_data[cur_section_key][cell.text] = {}  # The depth 1 dict (table row)
                else:
                    # Depth 2 dict (table cell & its value)
                    all_table_data[cur_section_key][section_data[0].text][header_keys[i]] = cell.text

    return all_table_data

# ========================================================================================
# ---------------------------------------Pitcher------------------------------------------
# ========================================================================================

def GetPitcherWinLoss(pitcher_anchor, opposing_team_anchor):

    # Win   @   HOME
    # Loss  @   HOME
    # Win       AWAY
    # Loss      AWAY
    # ERA       TOTAL

    endpoint = pitcher_anchor['href'].replace("player",  "player/splits")
    print(endpoint)

    # win loss home away
    pitcher_wl_ha = requests.get(endpoint, headers=header)

    if pitcher_wl_ha.status_code == 200:

        soup = BeautifulSoup(pitcher_wl_ha.content, 'html.parser')
        table_rows = soup.find("table", {"class": "tablehead"}).findAll("tr")

        all_pitcher_data = ScrapeStatsDataTableRows(table_rows)

        home_Ws = all_pitcher_data['By Breakdown']['Home']['W']
        home_Ls = all_pitcher_data['By Breakdown']['Home']['L']
        away_Ws = all_pitcher_data['By Breakdown']['Away']['W']
        away_Ls = all_pitcher_data['By Breakdown']['Away']['L']

        ERA = all_pitcher_data['Overall']['Total']['ERA']

        opponent_name = "TODODODO"
        ERA_vs_opponent = all_pitcher_data['By Opponent']['vs. {}'.format(opponent_name)]['IP']
        IP_vs_opponent = all_pitcher_data['By Opponent']['vs. {}'.format(opponent_name)]['IP']


        pprint.pprint(all_pitcher_data)



# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ----------------------------------------Team--------------------------------------------
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def GetHomeWinsLosses(team_anchor):
    #/mlb/team/_/name/mia/miami - marlins
    #mlb/team/stats/splits/_/name/det/detroit-tigers

    endpoint = team_anchor['href'].replace("team/", "team/stats/splits/")

    print(base_mlb + endpoint)

    wins_loses_html = requests.get(base_mlb + endpoint, headers=header)

    if wins_loses_html.status_code == 200:
        soup = BeautifulSoup(wins_loses_html.content, 'html.parser')

        return GetHomeAwayWL(soup)

def GetHomeAwayWL(soup):

    home_row_idx = GetRowIndexOfText(soup, "tablehead", "Home")
    away_row_idx = GetRowIndexOfText(soup, "tablehead", "Away")
    win_col_idx = GetTextIndexInHeader(soup, "colhead", "W")
    loss_col_idx = GetTextIndexInHeader(soup, "colhead", "L")

    table = soup.find("table", {"class": "tablehead"})
    all_rows = table.findAll("tr")

    home_wins = all_rows[home_row_idx].findAll("td")[win_col_idx].find(text=True)
    home_loses = all_rows[home_row_idx].findAll("td")[loss_col_idx].find(text=True)
    away_wins = all_rows[away_row_idx].findAll("td")[win_col_idx].find(text=True)
    away_loses = all_rows[away_row_idx].findAll("td")[loss_col_idx].find(text=True)
    print(home_wins)

    return home_wins, home_loses, away_wins, away_loses
        

def GetRowIndexOfText(soup, table_class, text):
    table = soup.find("table", {"class": table_class})

    all_rows = table.findAll("tr")

    candidate_row = table.find("td", text=text).parent  # Find the cell, want the row/parent

    return all_rows.index(candidate_row)

# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ----------------------------------------------------------------------------------------
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# --------------------------------team batting-------------------------------------------
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def GetAtBatsAndRunsTotals(team_anchor):

    # Row total for column AB
    # Row total for column R

    # Build the URL
    endpoint = os.path.dirname( team_anchor['href'].replace("team/", "team/stats/batting/") )

    bats_runs_html = requests.get(base_mlb+endpoint, headers=header)

    if bats_runs_html.status_code == 200:

        soup = BeautifulSoup(bats_runs_html.content, 'html.parser')

        return GetAtBatsRunsGeneric(soup)


def GetHomeBatsRunsSplits(team_anchor):
    # http: // www.espn.com / mlb / team / stats / batting / _ / name / det / split / 33

    #"TOTAL AB"

    # Build the URL
    endpoint = os.path.dirname( team_anchor['href'].replace("team/", "team/stats/batting/") )
    endpoint += "/split/33"  # ESPN code for batting @ HOME

    bats_runs_html = requests.get(base_mlb + endpoint, headers=header)

    if bats_runs_html.status_code == 200:

        soup = BeautifulSoup(bats_runs_html.content, 'html.parser')

        return GetAtBatsRunsGeneric(soup)


def GetAwayBatsRunsSplits(team_anchor):
    # http: // www.espn.com / mlb / team / stats / batting / _ / name / det / split / 33

    #"TOTAL AB"

    # Build the URL
    endpoint = os.path.dirname( team_anchor['href'].replace("team/", "team/stats/batting/") )
    endpoint += "/split/34"  # ESPN code for batting AWAY

    bats_runs_html = requests.get(base_mlb + endpoint, headers=header)

    if bats_runs_html.status_code == 200:

        soup = BeautifulSoup(bats_runs_html.content, 'html.parser')

        return GetAtBatsRunsGeneric(soup)

# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ----------------------------------------------------------------------------------------
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def GetTextIndexInHeader(soup, header_row_class, text):
    header_row = soup.find("tr", {"class": header_row_class}).findAll("td")
    header_cell_with_target_text = soup.findAll("td", text=text)
    return header_row.index(header_cell_with_target_text[0])

def GetAtBatsRunsGeneric(soup):

    at_bats_idx = GetTextIndexInHeader(soup, "colhead", "AB")
    runs_idx = GetTextIndexInHeader(soup, "colhead", "R")

    # Get the data from the correct columns in the totals row
    totals_row = soup.find("tr", {"class": "total"}).findAll("td")
    at_bats = totals_row[at_bats_idx].find(text=True)
    runs = totals_row[runs_idx].find(text=True)

    print(at_bats)
    print(runs)

    return at_bats, runs
