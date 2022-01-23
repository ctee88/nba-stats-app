"""
import endpoints
import libraries
"""
from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.endpoints import leaguestandings
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import sys

"""
STAT ABBRVS DISPLAY (needs to be 2 separate funcs - 1 for %, 1 for non-%??)
- Pass list(s) to conditional
- Return respective stats (e.g ['AST', 'TOV', 'BLK'...] and ['3PA', '3PM', '3PCT'...])
"""

#HELPER FUNCTION - RETURNS DF WITH ALL STATS FOR GIVEN YEAR
def fetch_df_stats(year):
	stats = json.loads(leagueleaders.LeagueLeaders(season=year).league_leaders.get_json())
	df = pd.DataFrame(stats['data'], columns=stats['headers'])

	return df

#FETCH SPECIFIC CUMULATIVE (CUME) STAT DATA FROM GIVEN YEAR
def fetch_stat_data(year, stat):
	df_stats = fetch_df_stats(year)
	df_stat = df_stats[['PLAYER', stat, 'GP', 'MIN']].sort_values(by=stat, ascending=False)

	return df_stat[:30]

#FETCH SPECIFIC % STAT DATA FROM GIVEN YEAR
def fetch_pct_stat_data(year, stat):
	df_pct_stats = fetch_df_stats(year)
	#Remove .upper() from here after finishing main.py (stat_string = input().upper())
	if stat.upper() == 'FGM':
		df_fgm = df_pct_stats[
			['PLAYER', stat, 'FGA', 'FG_PCT']
			].sort_values(by=stat, ascending=False)
		return df_fgm[:30]

	elif stat.upper() == 'FG3M':
		df_fg3m = df_pct_stats[
			['PLAYER', stat, 'FG3A', 'FG3_PCT']
			].sort_values(by=stat, ascending=False)
		return df_fg3m[:30]

	elif stat.upper() == 'FTM':
		df_ftm = df_pct_stats[
			['PLAYER', stat, 'FTA', 'FT_PCT']
			].sort_values(by=stat, ascending=False)
		return df_ftm[:30]

	else:
		return -1

#FETCH STANDINGS DATA FOR SPECIFIC YEAR
def fetch_standings(year):
	input_data = {}
	input_data['Teams'], input_data['Result'], input_data['Win/Loss'] = [], [], []

	standings = json.loads(leaguestandings.LeagueStandings(season=year).standings.get_json())

	for teams_data in standings['data']:
		#[3] = City Name, [4] = Team Name. Join for full team name.
		city_and_team = [teams_data[3], teams_data[4]]
		team_name = " ".join(city_and_team)

		#[12] = Wins, [13] = Losses
		input_data['Teams'].append(team_name)
		input_data['Result'].append('Wins')
		input_data['Win/Loss'].append(int(teams_data[12]))
		
		input_data['Teams'].append(team_name)
		input_data['Result'].append('Losses')
		input_data['Win/Loss'].append(int(teams_data[13]))
	
	df = pd.DataFrame(input_data)
	df_sorted = df.sort_values(by='Win/Loss')
	print(df)

	return df_sorted

#GRAPH FOR NON-% STATS (BAR CHART)
def plot_stat_totals(df, year, stat):
	fig = px.bar(
		df, x='PLAYER', y=[df[stat]],
		custom_data=[df['GP'], df['MIN']],
		title='Leaders in {} for the {} regular season'.format(stat, year),
		labels={'value': stat, 'PLAYER': 'Players'},
	)

	fig.update_traces(marker_line_color='rgb(8,48,107)',
		texttemplate=df[stat].to_list(), textposition='inside',
		hovertemplate="<br>".join([
			"Player: %{x}",
			"<b>Amount: %{y}</b>",
			"<b>Games Played: %{customdata[0]}</b>",
			"<b>Minutes Played: %{customdata[1]}</b>",
		])
	)
	fig.update_layout(xaxis_tickangle=-45, showlegend=False,
		uniformtext_minsize=8, uniformtext_mode='show'
	)

	fig.show()

#GRAPH FOR % STATS (OFFSET BAR CHARTS)
def plot_pct_stat(df, year):
	"""
	Input dfs' layout standardized by fetch_pct_stat_data() where:
	- col[0] == PLAYERS
	- col[1] == type of shot MADE (stat variable specified by user)
	- col[2] == type of shot ATTEMPTED
	- col[3] == %
	
	Declared the column names for readability.

	fig.update_yaxes(range[0, ATTEMPTS.max()*1.125])
	- Ensures both plots are scaled the same relative to the y-axis
	- Attempts > Made, max value will always be in Attempts column
	- 12.5% above max value to ensure that the max y-axis label is
	higher than max y-value on graph
	"""
	players = df.columns.values[0]
	made = df.columns.values[1]
	attempted = df.columns.values[2]
	pct = df.columns.values[3]

	#go hovertemplate customdata only works with np.array (different to px)
	pct_array = np.empty(shape=(len(df[pct]), 1, 1), dtype='object')
	pct_array[:,0] = np.array(df[pct]).reshape(-1, 1)

	fig = make_subplots(specs=[[{"secondary_y": True}]])
	
	fig.add_trace(go.Bar(
		x=df[players], y=df[made],
		customdata=pct_array,
		hovertemplate="<br>".join([
			"Player: %{x}",
			"<b>Made: %{y}</b>",
			"<b>%: %{customdata[0]:.3f}</b>",
		]),
		name=made, offsetgroup=1),
		secondary_y=False,
	)

	fig.add_trace(go.Bar(
		x=df[players], y=df[attempted],
		hovertemplate="<br>".join([
			"Player: %{x}",
			"<b>Attempted: %{y}</b>",
		]),
		name=attempted, offsetgroup=2),
		secondary_y=True,
	)

	fig.update_layout(
		title_text='Leaders in {} and their respective {} and {} for the {} regular season'.
		format(made, attempted, pct, year),
		xaxis_tickangle=-45
	)

	fig.update_traces(marker_line_color='rgb(8,48,107)')

	fig.update_xaxes(title_text='Players')
	fig.update_yaxes(title_text=made, secondary_y=False,
			range=[0, df[attempted].max()*1.125]
	)
	fig.update_yaxes(title_text=attempted, secondary_y=True,
			range=[0, df[attempted].max()*1.125]
	)

	fig.show()

#GRAPH FOR STANDINGS (STACKED BARS)
def plot_standings(df, year):
	fig = px.bar(
		df, x='Teams', y='Win/Loss', color='Result',
		title='NBA Standings for {} regular season'.format(year),
		labels={'Result': 'Wins/Losses', 'Teams': 'Team', 'Win/Loss': 'Number of Wins/Losses'}
	)

	fig.update_traces(marker_line_color='rgb(8,48,107)')
	fig.update_layout(barmode='stack', xaxis_tickangle=-45)
	fig.show()
