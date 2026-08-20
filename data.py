import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from links import *
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
warnings.simplefilter('ignore')
plt.style.use('ggplot')

def gather_data(SHEET, TAB, season):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET}/gviz/tq?tqx=out:csv&sheet={TAB}'
    raw_data = pd.read_csv(url)
    data = raw_data[['Session', 'Inning', 'Pitcher', 'Pitcher ID', 'Pitch', 'Swing', 'Diff', 'Old Result']].dropna().astype({'Pitch':'int'})
    data.rename(columns = {'Old Result':'Result'}, inplace = True)
    data['Session'] = data['Session'] + 100 * season
    return data

def gather_mln_data(SHEET, TAB):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET}/gviz/tq?tqx=out:csv&sheet={TAB}'
    raw_data = pd.read_csv(url)
    if 'Season' not in raw_data.columns:
        raw_data['Season'] = 12
    data = raw_data[['Session #', 'Inning', 'Pitcher', 'Pitcher ID', 'Pitch', 'Swing', 'Diff', 'Result', 'Season']].dropna().astype({'Pitch':'int', 'Swing':'int', 'Diff':'int', 'Pitcher ID':'int', 'Session #':'int', 'Season':'int'})
    data.rename(columns = {'Session #':'Session'}, inplace = True)
    data['Session'] = data['Session'] + 100 * data['Season']
    return data

def gather_catcher_data(SHEET, TAB):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET}/gviz/tq?tqx=out:csv&sheet={TAB}'
    raw_data = pd.read_csv(url)
    if 'Season' not in raw_data.columns:
        raw_data['Season'] = 13
    data = raw_data[['Session #', 'Inning', 'Catcher', 'Catcher ID', 'Throw', 'Season']].dropna().astype({'Throw':'int', 'Catcher ID':'int', 'Session #':'int', 'Season':'int'})
    data.rename(columns = {'Session #':'Session'}, inplace = True)
    data['Session'] = data['Session'] + 100 * data['Season']
    return data

def finite_distance(a, b):
    return min(abs(a - b), 1000 - abs(a - b))

def calc_delta(pitches):
    deltas = []
    deltas.append(0)

    for i in range(1, len(pitches.index)):
        forward_difference = (pitches['Pitch'].iloc[i] - pitches['Pitch'].iloc[i - 1]) % 1000
        backward_difference = (pitches['Pitch'].iloc[i - 1] - pitches['Pitch'].iloc[i]) % 1000

        if forward_difference <= backward_difference:
            deltas.append(forward_difference)
        else:
            deltas.append(-backward_difference)

    pitches['Delta'] = deltas
    return pitches

def old_mlr_data():
    mlr = pd.concat([gather_data(S4_S6_SHEET, S4_MLR, 4),
                     gather_data(S4_S6_SHEET, S5_MLR, 5), 
                     gather_data(S4_S6_SHEET, S6_MLR, 6), 
                     gather_data(S7_SHEET, S7_MLR, 7), 
                     gather_data(S8_SHEET, S8_MLR, 8),
                     gather_data(S9_SHEET, S9_MLR, 9),
                     gather_data(S10_SHEET, S10_MLR, 10),
                     gather_data(S11_SHEET, S11_MLR, 11)])
    mlr = mlr.map(lambda s: s.lower() if type(s) == str else s)
    return mlr

def old_milr_data():
    milr = pd.concat([gather_data(S4_S6_SHEET, S4_MILR, 4),
                      gather_data(S4_S6_SHEET, S5_MILR, 5), 
                      gather_data(S4_S6_SHEET, S6_MILR, 6), 
                      gather_data(S7_SHEET, S7_MILR, 7), 
                      gather_data(S8_SHEET, S8_MILR_A, 8),
                      gather_data(S8_SHEET, S8_MILR_B, 8),
                      gather_data(S9_SHEET, S9_MILR, 9),
                      gather_data(S10_SHEET, S10_MILR, 10),
                      gather_data(S11_SHEET, S11_MILR, 11)])
    milr = milr.map(lambda s: s.lower() if type(s) == str else s)
    return milr

def old_mln_data():
    mln = pd.concat([gather_mln_data(ARCHIVE_SHEET, ARCHIVE_TAB)])
    mln = mln.map(lambda s: s.lower() if type(s) == str else s)
    return mln

def old_catcher_data():
    catcher = pd.concat([gather_catcher_data(ARCHIVE_SHEET, ARCHIVE_TAB)])
    catcher = catcher.map(lambda s: s.lower() if type(s) == str else s)
    return catcher

def update_mlr_data(old_mlr):
    new_mlr = gather_data(S12_SHEET, S12_MLR, 12).map(lambda s: s.lower() if type(s) == str else s)
    mlr = pd.concat([old_mlr, new_mlr])
    mlr = calc_delta(mlr)
    return mlr

def update_milr_data(old_milr):
    new_milr = gather_data(S12_SHEET, S12_MILR, 12).map(lambda s: s.lower() if type(s) == str else s)
    milr = pd.concat([old_milr, new_milr])
    milr = calc_delta(milr)
    return milr

def update_mln_data(old_mln):
    new_mln = gather_mln_data(CURRENT_SHEET, MLN_TAB).map(lambda s: s.lower() if type(s) == str else s)
    mln = pd.concat([old_mln, new_mln])
    mln = calc_delta(mln)
    return mln

def update_catcher_data(old_catcher):
    new_catcher = gather_catcher_data(CURRENT_SHEET, MLN_TAB).map(lambda s: s.lower() if type(s) == str else s)
    catcher = pd.concat([old_catcher, new_catcher])
    return catcher

def set_pitcher(name, pitches):
    pitcher_id = pitches.loc[pitches['Pitcher'] == name, 'Pitcher ID']
    new_pitches = pitches.loc[pitches['Pitcher ID'] == pitcher_id.iloc[0]]
    new_pitches = calc_delta(new_pitches)
    return new_pitches

def set_catcher(name, throws):
    catcher_id = throws.loc[throws['Catcher'] == name, 'Catcher ID']
    new_throws = throws.loc[throws['Catcher ID'] == catcher_id.iloc[0]]
    return new_throws
    
def recent_list(name, league, pitches):
    num_rows = len(pitches.index)
    top_line = f'{name}\'s recent {league} pitches (**MOST RECENT FIRST**):\n'
    top_chart = '```\n+------+------+\n|   P  |   Δ  |\n+------+------+\n'
    numbers = ''

    if num_rows - 25 > 0:
        for i in range(25):
            pitch = str(pitches['Pitch'].iloc[(num_rows - 1) - i]).rjust(4, ' ')
            delta = str(pitches['Delta'].iloc[(num_rows - 1) - i]).rjust(4, ' ')
            numbers = numbers + f'| {pitch} | {delta} |\n'
    else:
        for i in range(num_rows):
            pitch = str(pitches['Pitch'].iloc[(num_rows - 1) - i]).rjust(4, ' ')
            delta = str(pitches['Delta'].iloc[(num_rows - 1) - i]).rjust(4, ' ')
            numbers = numbers + f'| {pitch} | {delta} |\n'

    end = '+------+------+```'
    output = top_line + top_chart + numbers + end
    return output

def pitch_trend(name, league, pitches):
    num_rows = len(pitches.index)

    if num_rows < 25:
        chart_pitches = pitches['Pitch'].iloc[0:num_rows]
    else:
        chart_pitches = pitches['Pitch'].iloc[num_rows - 25:num_rows]
        
    chart_pitches = chart_pitches.reset_index(drop=True)
    fig, ax = plt.subplots()
    ax.set_title(f'{name}\'s recent {league} pitches')
    ax.grid(True)
    ax.plot(chart_pitches.index, chart_pitches, color = 'b', marker = 'o', linestyle = '-')

    for x, y in enumerate(chart_pitches):
        ax.annotate(int(y), (x, y), textcoords='offset points', xytext=(0, 10), ha='center')

    return fig