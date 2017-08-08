import json
import pprint
import re
import datetime
import openpyxl

IS_SCRAPING_ESPN = True

# ================================================================================================================

n_previous_games = 4
n_games_per_sheet = 8

# ================================================================================================================

ratings_data_column_start = ord("l") - 96
col_offset_home_away = 2
col_offset_games = 4

header_row = 9
result_row = 10
runs_row = 11

# ================================================================================================================

profile_data_row_start = 5
profile_data_column_start = ord("d") - 96
profile_neat_layout_column_jump = (ord("q") - 96) - profile_data_column_start  # second set of games starts at col Q

profile_row_offset_home_away = 1
profile_row_offset_game = 3

# ================================================================================================================
win_loss_key = "W/L"
team_score_key = "Score"

pitcher_name_key = 'name'

pitcher_win_loss_key = "RESULT" if IS_SCRAPING_ESPN else "DECISION"

# ================================================================================================================

def WriteHeader(team_data, worksheet, col_offset=0, is_home=None):

    if is_home is None:
        home_away = "TEAM: "
    elif is_home:
        home_away = "HOME: "
    else:
        home_away = "AWAY: "

    worksheet.cell(column=col_offset, row=header_row, value="{} {}".format(home_away, team_data['team_id']))


def WriteResult(team_data, worksheet, col_offset=0):

    for i in range(n_previous_games):
        worksheet.cell(column=col_offset + i, row=result_row, value="{}".format( team_data[ win_loss_key ][i] ))

def WriteRuns(team_data, worksheet, col_offset=0):

    for i in range(n_previous_games):
        score = team_data[ team_score_key ][i]
        score = re.search(r'\d+', score).group()  # get only the first number using .search()
        worksheet.cell(column=col_offset + i, row=runs_row, value=score)

# ================================================================================================================

def WriteProfile(pitcher_data, worksheet, row_offset=0, col_offset=0):

    worksheet.cell(column=col_offset, row=row_offset, value=pitcher_data['team_id'])
    worksheet.cell(column=col_offset + 1, row=row_offset, value=pitcher_data[ pitcher_name_key ])

    # Write previous decisions
    for i in range(n_previous_games):
        try:
            worksheet.cell(column=col_offset + 2 + i, row=row_offset, value=pitcher_data[ pitcher_win_loss_key ][i])
        except:
            worksheet.cell(column=col_offset + 2 + i, row=row_offset, value="NO DATA")

    # print("\n\n", "="*50, "\n")

# ================================================================================================================


def WriteDataToExcel(data):

    base = openpyxl.load_workbook(filename="worksheets/RUN-SHEET-BASE.xlsx")

    # = = = = = = = = = = = = = = = = = = = = = = RATINGS  = = = = = = = = = = = = = = = = = =

    all_ratings = [base['RATINGS - 1'], base['RATINGS - 2']]

    print(base.sheetnames)

    total_col_offset = -1
    sheet_idx = -1

    for i, game in enumerate(data):

        if i % n_games_per_sheet == 0:                                      # Aneryin spreads games over sheets, so do this too...
            sheet_idx += 1                                                  # Go to the next sheet
            total_col_offset = ratings_data_column_start + 1                # Start at the beginning column

        if sheet_idx >= len(all_ratings):
            break

        ratings = all_ratings[sheet_idx]

        home = game['HOME']
        away = game['AWAY']

        WriteHeader(home, ratings, total_col_offset - 1, is_home=True)
        WriteResult(home, ratings, total_col_offset)
        WriteRuns(home, ratings, total_col_offset)

        total_col_offset += n_previous_games + col_offset_home_away

        WriteHeader(away, ratings, total_col_offset - 1, is_home=False)
        WriteResult(away, ratings, total_col_offset)
        WriteRuns(away, ratings, total_col_offset)

        total_col_offset += n_previous_games + col_offset_games

    # = = = = = = = = = = = = = = = = = = = = = PROFILING  = = = = = = = = = = = = = = = = = = = =

    profiling = base['PROFILING']

    pitcher_row = -1
    pitcher_col = -1

    for i, game in enumerate(data):

        if i % n_games_per_sheet == 0:  # Aneryin spreads games over sheets, so do this too...
            pitcher_row = profile_data_row_start
            pitcher_col = profile_data_column_start + (profile_neat_layout_column_jump * round(i/n_games_per_sheet, 0))

        try:
            home = game['HOME']['pitcher']
            away = game['AWAY']['pitcher']
        except:
            pitcher_row += profile_row_offset_home_away
            pitcher_row += profile_row_offset_game
            continue

        WriteProfile(home, profiling, pitcher_row, pitcher_col)

        pitcher_row += profile_row_offset_home_away

        WriteProfile(away, profiling, pitcher_row, pitcher_col)

        pitcher_row += profile_row_offset_game

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

    base.save("MLB_{}.xlsx".format(datetime.datetime.today().strftime('%Y-%m-%d')))


# ================================================================================================================
#
# if __name__ == "__main__":
#
#     with open('json/temp_espn_game_data.json', 'r') as fp:
#         data = json.load(fp)
#         # pprint.pprint(data)
#         WriteDataToExcel(data)