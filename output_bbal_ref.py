import xlsxwriter
import json
import pprint
import re
import datetime

#
# CODE GOLF
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

n_previous_games = 5
col_offset = n_previous_games + 2

header_row = 0
result_row = 1
runs_row = 2


formats = {}

###################################################################################################v

def WriteHeaderData(team_data, worksheet, col_offset=0):

    worksheet.write(header_row, col_offset+0, "TEAM: " + team_data['team_id'], formats['default'])     # team name

    for i in range(n_previous_games):
        worksheet.write(header_row, col_offset+1+i, ordinal(i+1), formats['default'])

def WriteResultData(team_data, worksheet, col_offset=0):

    worksheet.write(result_row, col_offset+0, "RESULT", formats['default'])

    for i in range(5):
        worksheet.write(result_row, col_offset+i+1, team_data['W/L'][i], formats['default'])


def WriteRunsData(team_data, worksheet, col_offset=0):

    worksheet.write(runs_row, col_offset+0, "RUNS", formats['default'])

    for i in range(5):
        score = team_data['Score'][i]
        score = re.search(r'\d+', score).group()                        # get only the first number using .search()
        worksheet.write(runs_row, col_offset+i+1, score, formats['default'])

###################################################################################################v

def WriteDataToExcel(data):

    global formats

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('{}_MLB.xlsx'.format(datetime.datetime.today().strftime('%Y-%m-%d')))
    worksheet = workbook.add_worksheet()

    formats['default'] = workbook.add_format({'bold': True, 'center_across': True})
    formats['border'] = workbook.add_format({'right': True})

    total_col_offset = 0

    for game in data:
        home = game['HOME']
        away = game['AWAY']

        WriteHeaderData(home, worksheet, total_col_offset)
        WriteResultData(home, worksheet, total_col_offset)
        WriteRunsData(home, worksheet, total_col_offset)

        total_col_offset += col_offset

        WriteHeaderData(away, worksheet, total_col_offset)
        WriteResultData(away, worksheet, total_col_offset)
        WriteRunsData(away, worksheet, total_col_offset)

        total_col_offset += col_offset + 2




    workbook.close()
#
# with open('temp_game_data.json', 'r') as fp:
#     data = json.load(fp)
#
#     WriteDataToExcel(data)
#
#
#
#     pprint.pprint(data)