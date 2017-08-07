from bs4 import BeautifulSoup
from bs4 import Comment

import requests

import re
import pprint
import json
import datetime
import os

from output_bbal_ref import WriteDataToExcel

pp = pprint.PrettyPrinter(indent=4)

base_mlb = "http://www.espn.com"
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
def GetSchedule():
    # So you go to the scheduel

    # For eahc game on a given day follow:
    #       The link for each team and get
    #                       the results of their last N games (win or loss)
    #                       the number of runs scored (first number in the %d-%d next to W/L)
    #       The link for each pitcher and get their last results too

    schedule_url = base_mlb + "/mlb/schedule/_/date/{}".format(datetime.datetime.today().strftime('%Y%m%d'))
    print(schedule_url)

    sched_html = requests.get(schedule_url, headers=header)

    all_games = []

    count = 0

    if sched_html.status_code == 200:

        soup = BeautifulSoup(sched_html.content, 'html.parser')

        schedule_container = soup.find("div", {"id": "sched-container"})

        games_on_a_day = schedule_container.findAll("table", {"class": "schedule"})  # games are distributed over tables

        for games in games_on_a_day:
            game_rows = games.findAll("tr", {"class": ["odd", "even"]})             # get all rows

            for game in game_rows:

                print("Analysing game {}".format(count))
                count += 1

                game_data = GetGameData(game)
                if game_data is not None:

                    all_games.append(game_data)


            print("` " * 100)

    return all_games


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def GetGameData(game):
    team_data = game.findAll("a", {"class": "team-name"})  # get team names
    pitcher_data = game.findAll("a", {"name": "&lpos=mlb:schedule:player"})
    game_date = game.findAll("td", {"data-behavior": "date_time"})  # will be none for non-upcoming games

    if len(game_date) == 0:
        return None

    game_data = {}

    game_data["SOURCE"] = "ESPN"

    for i, side in enumerate(["AWAY", "HOME"]):

        print('Get Game Data: {}'.format(side))

        game_data[side] = GetTeamData(team_data[i])  # format is "AWAY @ HOME"

        game_data[side]['pitcher'] = GetPitcherData(pitcher_data[i])
        game_data[side]['pitcher']['team_id'] = game_data[side]['team_id']

    print("-"*100)

    return game_data

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def GetPitcherData(pitcher_anchor):

    print("\tGet Pitcher Data: {}".format(pitcher_anchor.find(text=True)))

    pitcher_data = {}

    pitcher_data["name"] = pitcher_anchor.find(text=True)

    team_html = requests.get(pitcher_anchor['href'], headers=header)

    if team_html.status_code == 200:

        soup = BeautifulSoup(team_html.content, 'html.parser')

        last_ten_games = soup.findAll("div", {"class": "player-card"})[0].findAll("table")[0].findAll("tr")

        header_reference = []                   # allows you to track header data by index. Is there a cleaner way?

        for game in last_ten_games:

            _class = game.get("class")[0]

            if _class == 'stathead':
                continue
            elif _class == 'colhead':           # This is the header row. Populate dict keys here.

                for header_cell in game.findAll("td"):
                    header_col_name = header_cell['title'] if header_cell.has_attr('title') else ''.join(header_cell.findAll(text=True))
                    pitcher_data[header_col_name] = []
                    header_reference.append(header_col_name)

            else:
                                                # Standard case: populate each dict-keyed array with data...
                for i, data_cell in enumerate(game.findAll("td")):
                    pitcher_data[ header_reference[i] ].append( ''.join(data_cell.findAll(text=True)) )

    # Split 'W 2-5' into 'W' & '2-5'
    pitcher_data['SCORE'] = [x[2:] for x in pitcher_data['RESULT']]
    pitcher_data['RESULT'] = [x[0] for x in pitcher_data['RESULT']]

    return pitcher_data


def GetTeamData(team_anchor):

    print("\tGet Team Data: {}".format(team_anchor.find("abbr")["title"]))

    team_data = {
        "team_id": team_anchor.find("abbr")["title"],
        "W/L": [],
        "Score": [],
        "Opp": [],
        "Date & Box": [],
    }

    # Modify the URL to get to the FULL stats page
    full_schedule_endpoint = os.path.dirname( team_anchor['href'].replace("team", "team/schedule") )
    team_url = base_mlb+full_schedule_endpoint
    # team_url = base_mlb+team_anchor['href']

    team_html = requests.get(team_url, headers=header)

    if team_html.status_code == 200:
        soup = BeautifulSoup(team_html.content, 'html.parser')

        game_rows = soup.findAll("tr")

        ### This is a fragile method...
        ### Column header positions as of August 2017...
        date_col = 0
        opponent_col = 1
        result_col = 2
        winning_pitcher_col = 3
        losing_pitcher_col = 3

        for game in game_rows:
            cells = game.findAll("td")

            if len(cells) > 1:
                opposing_team = cells[ opponent_col ].findAll(text=True)
                result_and_score = cells[ result_col ].findAll(text=True)
                date = cells[date_col].findAll(text=True)

                if len(opposing_team) == 2 and len(result_and_score) == 2 and len(date) == 1:

                    win_or_lose = result_and_score[0]  # laid out as something like:  [W, 5-2]
                    score = result_and_score[1]
                    date = date[0]
                    opposing_team = ' '.join(opposing_team)

                    team_data["W/L"].append(win_or_lose)
                    team_data["Score"].append(score)
                    team_data["Date & Box"].append(date)
                    team_data["Opp"].append(opposing_team)

    return team_data

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

if __name__ == "__main__":

    with open('temp_espn_game_data.json', 'w') as fp:
        data = GetSchedule()
        # pprint.pprint(data)
        json.dump(data, fp)


        # WriteDataToExcel(data)
