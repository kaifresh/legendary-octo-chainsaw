from bs4 import BeautifulSoup
import requests

base_url = "http://www.espn.com.au"

def GetRecentResults(url):

    print(url)

    url = GetScheduleURLFromTeamURL(url)

    results_html = requests.get(base_url + url)


    if results_html.status_code == 200:

        soup = BeautifulSoup(results_html.content, 'html.parser')

        print(results_html.status_code)

        row = soup.findAll("a", {"name": "&lpos=mlb:teamclubhouse:schedule:regular"})

        # print(row)

        for i, r in enumerate(row):
            # print(r)
            try:
                opposing_team = r.findAll("div", {"class": "game-info"})[0].get_text()
                print(opposing_team)
                result = r.findAll("div", {"class": "game-result"})[0].get_text()
                score = r.findAll("div", {"class": "score"})[0].get_text()

                print(" played {}. Result was {}. Score was {}".format(opposing_team, result, score))
            except Exception as e:

                print("Error: {}".format(e))

def GetSchedule():

    '''
    Structure of the url:
    http://www.espn.com.au/mlb/schedule/_/date/20170709
    '''

    schedule_html = requests.get(base_url+"/mlb/schedule")

    if schedule_html.status_code == 200:

        soup = BeautifulSoup(schedule_html.content, 'html.parser')

        # print(soup.prettify())
        # row = soup.select('tr.odd td a span')
        # print(row)

        row = soup.findAll("a", {"name": "&lpos=mlb:schedule:team", "class": "team-name"})

        for i, r in enumerate(row):

            GetRecentResults(r['href'])
            break

            # print(r)
            team_name = r.find("span").contents
            team_link = r['href']
            print(team_name, team_link )

            # even = home, odd = away

            if i % 2 == 0:
                print("is playing: ")
            else:
                print("\n")
            # print("\n\n")


def GetScheduleURLFromTeamURL(url):
    '''

    /mlb/team/         _/name/mil/milwaukee-brewers
    /mlb/team/schedule/_/name/mil/milwaukee-brewers
    '''
    print(url)

    return url.replace("_/", "schedule/_/")


GetSchedule()