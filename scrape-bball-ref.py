from bs4 import BeautifulSoup
import requests
import re
from bs4 import Comment
import pprint


pp = pprint.PrettyPrinter(indent=4)

base_mlb = "https://www.baseball-reference.com"
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

def GetSchedule():

    schedule_url = base_mlb+"/leagues/MLB-schedule.shtml"

    sched_html = requests.get(schedule_url, headers=header)

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

            GetPreviewStats(preview_url)

def GetPreviewStats(preview_url):

    preview_html = requests.get(preview_url, headers=header)

    soup = BeautifulSoup(preview_html.content, 'html.parser')

    # NOTE:
    # For some nuts reason, the last 10 games data IS IN A COMMENT when you get the raw HTML
    # Normally, as the page loads in the browser, some javascript formats it into a proper table, but we dont have that here
    # Given how shit it is, this may change
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    preview_data = {}

    # print(comments)
    for c in comments:

        comment_soup = BeautifulSoup(c, 'html.parser')
        tables = comment_soup.findAll("table", {"id": re.compile('last10_.*')}) # Tables we want are like id=last10_NYY

        if len(tables) > 0:

            last10 = tables[0]
            team_id = last10.get("id")[-3:]

            team_data = {}

            header_indexed = []                                         # store the headers in order (to infer this from the data cells)

            for header_cell in last10.find("thead").find("tr"):
                header_text = header_cell.text.strip()
                team_data[header_text] = []
                header_indexed.append(header_text )

            game_rows = last10.find("tbody").findAll("tr")
            for r in game_rows:
                game_results = r.findAll('td')#[3].text.strip()

                for i, cell in enumerate(game_results):
                    team_data[header_indexed[i]].append(cell.text.strip())

            print("TEAM DATA: {}".format(team_data))
            print("="*50)

            preview_data[team_id] = team_data

    pp.pprint(preview_data)
    exit()
    return preview_data


GetSchedule()