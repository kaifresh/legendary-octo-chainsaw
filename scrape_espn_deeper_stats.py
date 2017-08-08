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

# ========================================================================================
# ---------------------------------------Pitcher------------------------------------------
# ========================================================================================

def GetPitcherDeepStats(pitcher_anchor, opposing_team_anchor):

    # print("\tGet Pitcher Deep Stats: {}".format(pitcher_anchor.find(text=True)))

    # Win   @   HOME
    # Loss  @   HOME
    # Win       AWAY
    # Loss      AWAY
    # ERA       TOTAL

    endpoint = pitcher_anchor['href'].replace("player",  "player/splits")

    # win loss home away
    pitcher_wl_ha = requests.get(endpoint, headers=header)

    if pitcher_wl_ha.status_code == 200:

        soup = BeautifulSoup(pitcher_wl_ha.content, 'html.parser')
        table_rows = soup.find("table", {"class": "tablehead"}).findAll("tr")

        all_pitcher_data = ScrapeStatsDataTableRows(table_rows)
        #
        # home_Ws = all_pitcher_data['By Breakdown']['Home']['W']
        # home_Ls = all_pitcher_data['By Breakdown']['Home']['L']
        # away_Ws = all_pitcher_data['By Breakdown']['Away']['W']
        # away_Ls = all_pitcher_data['By Breakdown']['Away']['L']
        # ERA = all_pitcher_data['Overall']['Total']['ERA']
        # opponent_name = opposing_team_anchor.find("abbr").text
        #
        # try:
        #     ERA_vs_opponent = all_pitcher_data['By Opponent']['vs. {}'.format(opponent_name)]['IP']
        #     IP_vs_opponent = all_pitcher_data['By Opponent']['vs. {}'.format(opponent_name)]['IP']
        # except:
        #     ERA_vs_opponent = None,
        #     IP_vs_opponent = None

        return all_pitcher_data
        # return home_Ws, home_Ls, away_Ws, away_Ls, ERA, ERA_vs_opponent, IP_vs_opponent, all_pitcher_data
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ----------------------------------------Team Wins/Losses--------------------------------------------
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def GetHomeWinsLosses(team_anchor):
    # print("\tGet Home Wins & Losses: {}".format(team_anchor.find(text=True)))

    endpoint = team_anchor['href'].replace("team/", "team/stats/splits/")

    wins_loses_html = requests.get(base_mlb + endpoint, headers=header)

    if wins_loses_html.status_code == 200:
        soup = BeautifulSoup(wins_loses_html.content, 'html.parser')

        batting_table_rows = soup.find("table", {"class": "tablehead"}).findAll("tr")

        all_batting_rows = ScrapeStatsDataTableRows(batting_table_rows)['NAME']
        #
        # home_Ws = all_batting_rows['Home']['W']
        # home_Ls = all_batting_rows['Home']['L']
        # away_Ws = all_batting_rows['Away']['W']
        # away_Ls = all_batting_rows['Away']['L']

        return all_batting_rows
        # return home_Ws, home_Ls, away_Ws, away_Ls, all_batting_rows

# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# --------------------------------Team Batting-------------------------------------------
# - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def GetAtBatsAndRunsTotals(team_anchor):

    # print("\tGet At Bats And Runs Totals: {}".format(team_anchor.find(text=True)))

    return GetAtBatsRunsGenericWrap( team_anchor['href'] )

def GetHomeBatsRunsSplits(team_anchor):

    # print("\tGet HOME At Bats And Runs Splits: {}".format(team_anchor.find(text=True)))

    return GetAtBatsRunsGenericWrap(team_anchor['href'], "/split/33")

def GetAwayBatsRunsSplits(team_anchor):

    # print("\tGet AWAY At Bats And Runs Splits: {}".format(team_anchor.find(text=True)))

    return GetAtBatsRunsGenericWrap(team_anchor['href'], "/split/34")

def GetAtBatsRunsGenericWrap(href, extra_endpoint=""):
    endpoint = os.path.dirname(href.replace("team/", "team/stats/batting/"))
    endpoint += extra_endpoint

    bats_runs_html = requests.get(base_mlb + endpoint, headers=header)

    if bats_runs_html.status_code == 200:
        soup = BeautifulSoup(bats_runs_html.content, 'html.parser')

        return GetAtBatsRunsGeneric(soup)

def GetAtBatsRunsGeneric(soup):
    batting_table_rows = soup.find("table", {"class": "tablehead"}).findAll("tr")

    all_batting_rows = ScrapeStatsDataTableRows(batting_table_rows)['NAME']

    # at_bats = all_batting_rows['Totals']['AB']
    # runs = all_batting_rows['Totals']['R']

    return all_batting_rows
    # return at_bats, runs, all_batting_rows

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#    Generic scraper...
#       Requires a table format that has classes of:
#            stathead        name of the table (unused)
#            colhead         row where each column is the name of a stat
#            (even|odd)row   row where [0] is the name of the category and,
#                            each cell is the data corresponding to the corresponding stat in colhead

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def ScrapeStatsDataTableRows(table_rows):

    '''
            Pass in the rows of a table... ie elemenet.findAll("tr")

                --- HOW THIS WORKS ---
            You are making a 3 tiered dictionary
            depth 0 = each table
            depth 1 = the rows of the table
            depth 2 = the columns of the tables
            values of depth 2 = the cell data...

    '''

    all_table_data = {}
    cur_section_key = ""
    header_keys = []

    for row in table_rows:

        try:   # sometimes the table row class is missing, by default treat it as a data row. May create errors...
            row_class = row.get("class")[0]
        except:
            row_class = None

        if row_class == "colhead":  # Store the keys for each data cell (i.e. columns of header)

            section_header = row.findAll("td")
            cur_section_key = section_header[0].text        # Key for the depth 1 dictionary

            if cur_section_key not in all_table_data:       # If two sections have the same name, you wont overwrite old data
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