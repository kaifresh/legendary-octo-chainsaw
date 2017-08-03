from bs4 import BeautifulSoup
import requests
import re
from bs4 import Comment
import pprint
import json

from output_bbal_ref import WriteDataToExcel

pp = pprint.PrettyPrinter(indent=4)

base_mlb = "https://www.baseball-reference.com"
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

def GetSchedule():

    schedule_url = base_mlb+"/leagues/MLB-schedule.shtml"

    sched_html = requests.get(schedule_url, headers=header)

    all_games = []

    if sched_html.status_code == 200:

        soup = BeautifulSoup(sched_html.content, 'html.parser')

        today = soup.find("span", {"id": "today"}).parent.parent #.findNext("div")

        games = today.findAll("p" , {"class": "game"})

        for g in games:
            print("*************************")
            # print(g)

            teams = g.findAll("a")
            preview = g.findAll("a", text="Preview")
            print(teams)

            print(preview)

            preview_url = base_mlb + preview[0]['href']

            all_games.append(GetPreviewStats(preview_url))

            # break
    #
    # pp.pprint(all_games)
    # WriteDataToExcel(all_games)
    with open('temp_game_data.json', 'w') as fp:
        json.dump(all_games, fp)

def GetPreviewStats(preview_url):

    preview_html = requests.get(preview_url, headers=header)

    soup = BeautifulSoup(preview_html.content, 'html.parser')

    pitcher_names = soup.findAll("span", {"class": "section_anchor", "data-label": re.compile('.*Stats')})
    pitcher_names = [x['data-label'].replace(" Stats", "") for x in pitcher_names]

    # NOTE:
    # For some nuts reason, the last 10 games data IS IN A COMMENT...
    # I imagine that, as the page loads in the browser, some javascript formats it into a proper table...
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    game_data = {}

    pitcher_idx = 0

    for c in comments:

        comment_soup = BeautifulSoup(c, 'html.parser')

        # - - - - - - - - - - - - - - - - - - TEAM STATS - - - - - - - - - - - - - - - - - -

        tables = comment_soup.findAll("table", {"id": re.compile('last10_.*')})  # We want tables like 'id=last10_NYY'

        if len(tables):

            last10 = tables[0]

            team_data = {
                "team_id": last10.get("id")[-3:]                # last10_**NYY**
            }

            table_header = last10.find("thead").find("tr").findAll("th")

            for header_cell in table_header:                                 # Get the column names from the header -> keys
                header_text = header_cell.text.strip()
                team_data[header_text] = []

            game_rows = last10.find("tbody").findAll("tr")             # Get actual data from table rows -> values
            for r in game_rows:
                game_results = r.findAll('td')
                for i, pitcher_stat in enumerate(game_results):
                    team_data[table_header[i].text].append(pitcher_stat.text.strip())    # Store relevant data for the key in an []

            if len(game_data) == 0:
                game_data["AWAY"] = team_data
            else:
                game_data["HOME"] = team_data                        # HOME is always second in basketball reference

        # - - - - - - - - - - - - - - - - - - PITCHER STATS - - - - - - - - - - - - - - - - - -

        tables = comment_soup.findAll("table", {"id": re.compile('^sp_.*')})

        if len(tables):

            pitcher = tables[0]

            pitcher_data = {
                "name": pitcher_names[pitcher_idx]
            }

            did_see_spacer = False
            spacer_idx = -1

            pitcher_rows = pitcher.find("tbody").findAll("tr")  # Get actual data from table rows -> values
            for i, r in enumerate(pitcher_rows):

                # First few rows are historical data, we dont want that
                if not did_see_spacer and r.get("class") is not None and "spacer" in r.get("class"):
                    did_see_spacer = True
                    spacer_idx = i

                if did_see_spacer and i > spacer_idx+1:     # Skip the spacer & 1 row!

                    for pitcher_stat in r.findAll('td'):

                        try:
                            stat = pitcher_stat['data-stat']        # Unlike team stats, the name of the stat is an attr
                        except:
                            continue                                # Sometimes there is an extra column in the html. Skip.

                        if stat not in pitcher_data:
                            pitcher_data[stat] = []

                        pitcher_data[stat].append(pitcher_stat.text.strip())

            if pitcher_idx == 0:
                pitcher_data['team_id'] = game_data["AWAY"]["team_id"]
                game_data["AWAY"]['pitcher'] = pitcher_data
            else:
                game_data["HOME"]['pitcher'] = pitcher_data
                pitcher_data['team_id'] = game_data["HOME"]["team_id"]
            pitcher_idx += 1

    return game_data

if __name__ == "__main__":
    GetSchedule()