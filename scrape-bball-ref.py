from bs4 import BeautifulSoup
import requests
import re
from bs4 import Comment
import pprint
import json
# from .scrape_mlb import
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
    WriteDataToExcel(all_games)
    # with open('temp_game_data.json', 'w') as fp:
    #     json.dump(all_games, fp)

def GetPreviewStats(preview_url):

    preview_html = requests.get(preview_url, headers=header)

    soup = BeautifulSoup(preview_html.content, 'html.parser')

    # NOTE:
    # For some nuts reason, the last 10 games data IS IN A COMMENT...
    # I imagine that, as the page loads in the browser, some javascript formats it into a proper table...
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    preview_data = {}

    for c in comments:

        comment_soup = BeautifulSoup(c, 'html.parser')
        tables = comment_soup.findAll("table", {"id": re.compile('last10_.*')})  # We want tables like 'id=last10_NYY'

        if len(tables) > 0:

            last10 = tables[0]

            team_data = {
                "team_id": last10.get("id")[-3:]                # last10_**NYY**
            }

            theader = last10.find("thead").find("tr").findAll("th")

            for header_cell in theader:                                 # Get the column names from the header -> keys
                header_text = header_cell.text.strip()
                team_data[header_text] = []

            game_rows = last10.find("tbody").findAll("tr")             # Get actual data from table rows -> values
            for r in game_rows:
                game_results = r.findAll('td')
                for i, cell in enumerate(game_results):
                    team_data[theader[i].text].append(cell.text.strip())    # Store relevant data for the key in an []

            if len(preview_data) == 0:
                preview_data["AWAY"] = team_data
            else:
                preview_data["HOME"] = team_data                        # HOME is always second in basketball reference

    return preview_data

if __name__ == "__main__":
    GetSchedule()