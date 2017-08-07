from bs4 import BeautifulSoup
import requests
import re
from bs4 import Comment
import pprint
import json
import datetime
import os

from output_bbal_ref import WriteDataToExcel

pp = pprint.PrettyPrinter(indent=4)

base_mlb = "http://www.espn.com"
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}




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

    if sched_html.status_code == 200:

        soup = BeautifulSoup(sched_html.content, 'html.parser')

        schedule_container = soup.find("div", {"id": "sched-container"})

        games_on_a_day = schedule_container.findAll("table", {"class": "schedule"})  # games are distributed over tables

        for games in games_on_a_day:
            game_rows = games.findAll("tr", {"class": ["odd", "even"]})             # get all rows

            for game in game_rows:

                game_data = GetGameData(game)
                if game_data is not None:
                    all_games.append(game_data)


            print("` " * 100)



def GetGameData(game):
    team_data = game.findAll("a", {"class": "team-name"})  # get team names
    pitcher_data = game.findAll("a", {"name": "&lpos=mlb:schedule:player"})
    game_date = game.findAll("td", {"data-behavior": "date_time"})  # will be none for non-upcoming games

    if len(game_date) == 0:
        return None

    game_data = {}
    game_data["HOME"] = GetTeamData(team_data[1])  # format is "AWAY @ HOME"





def GetTeamData(team_anchor):
    print(team_anchor)

    team_data = {
        "team_id": team_anchor.find("abbr")["title"],
        "W/L": [],
        "Score": [],
        "Opp": [],
        "Date & Box": [],
    }
    print(team_data)

    # team_url = base_mlb+team_anchor['href']
    full_schedule_endpoint = os.path.dirname( team_anchor['href'].replace("team", "team/schedule") )
    team_url = base_mlb+full_schedule_endpoint

    print(team_url)

    team_html = requests.get(team_url, headers=header)

    if team_html.status_code == 200:
        soup = BeautifulSoup(team_html.content, 'html.parser')

        game_rows = soup.findAll("tr")

        ### August 2017, column header positions
        date_col = 0
        opponent_col = 1
        result_col = 2
        winning_pitcher_col = 3
        losing_pitcher_col = 3



        for game in game_rows:
            print("~ " * 100)
            # print(game.prettify())


            # Who / Where
            # Score
            # W/L

            cells = game.findAll("td")


            if len(cells) > 1:
                opposing_team = cells[ opponent_col ].findAll(text=True)
                result_and_score = cells[ result_col ].findAll(text=True)
                date = cells[date_col].findAll(text=True)


                if len(opposing_team) == 2 and len(result_and_score) == 2 and len(date) == 1:

                    print(date)
                    print(opposing_team)
                    print(result_and_score)

                    result = result_and_score[0]
                    score = result_and_score[1]
                    date = date[0]
                    opposing_team = ' '.join(opposing_team)






            # print("." * 200)
            # win_lose = game.findAll("li", {"class": "game-status"})
            # score = game.findAll("li", {"class": "score"})
            # opposing_team = game.findAll("ul", {"class": "game-schedule"})
            #
            # if len(win_lose) > 0 and len(score) > 0 and len(opposing_team) > 0 :
            #
            #     # win_lose = win_lose[0].find(text=True)
            #     # score = score[0].find(text=True)
            #     # opposing_team = opposing_team[0].find(text=True)
            #
            #
            #     print(win_lose)
            #
            #     print(score)
            #     print(opposing_team)
            #     print("." * 200)



    # team_html = requests.get(team_url, headers=header)

    # if team_html.status_code == 200:
    #     soup = BeautifulSoup(team_html.content, 'html.parser')
    #
    #     previous_games = soup.find("section", {"class": "club-schedule"})
    #
    #     prev_games_info = previous_games.findAll("div", {"class": "game-meta"})
    #
    #     for game in prev_games_info:
    #
    #         win_lose = game.find("div", "game-result_and_score")
    #         score = game.find("div", "score")
    #
    #         opposing_team = game.parent.find("div", {"class": "game-info"})
    #         print(opposing_team)
    #
    #         if win_lose is not None and score is not None:
    #             team_data["W/L"].append( win_lose.find(text=True) )
    #             team_data["Score"].append( score.find(text=True) )
    #
    #
    #         # print(score)
    #         #
    #         # except:
    #         #     pass
    #
    # print("." * 200)
    #
    exit()
print("=" * 200)

if __name__ == "__main__":
    GetSchedule()