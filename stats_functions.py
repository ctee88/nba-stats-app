"""
import endpoints
import libraries
"""
from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.endpoints import leaguestandings
from plotly.subplots import make_subplots
import pandas as pd
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
	df_stat = df_stats[['PLAYER', stat]].sort_values(by=stat, ascending=False)

	return df_stat[:30]

#FETCH SPECIFIC % STAT DATA FROM GIVEN YEAR
def fetch_pct_stat_data(year, stat):
	df_pct_stats = fetch_df_stats(year)

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

#GRAPH FOR NON-% STATS (BAR CHART)
def plot_stat_totals(df, year, stat):
	fig = px.bar(df, x='PLAYER', y=[df[stat]],
			title='Leaders in {} for the {} regular season'.format(stat, year),
			labels={'value': stat, 'PLAYER': 'Player', 'variable': stat},
			)

	fig.update_traces(texttemplate=df[stat].to_list(), textposition='inside')
	fig.update_layout(xaxis_tickangle=-45, showlegend=False,
			uniformtext_minsize=8, uniformtext_mode='show'
			)
	fig.show()

#GRAPH FOR % STATS (OFFSET BAR CHARTS)
def plot_pct_stat(df, year, stat):
	pass

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

	return df_sorted

#GRAPH FOR STANDINGS (STACKED BARS)
def plot_standings(df, year):
	fig = px.bar(df, x='Teams', y='Win/Loss', color='Result',
		title='NBA Standings for {} regular season'.format(year),
		labels={'Result': 'Wins/Losses', 'Teams': 'Team', 'Win/Loss': 'Number of Wins/Losses'}
		)

	fig.update_layout(barmode='stack', xaxis_tickangle=-45)
	fig.show()

#Standings funcs test
# standings_1920 = fetch_standings('2019-20')
# plot_standings(standings_1920, '2019-20')

# NON-% funcs test
# ast_df = fetch_stat_data('2021-22', 'STL')
# plot_stat_totals(ast_df, '2021-22', 'STL')

#% funcs test
# df_fgm = fetch_pct_stat_data('2021-22', 'FGM')
# print(df_fgm)

# df_fg3m = fetch_pct_stat_data('2021-22', 'FG3M')
# print(df_fg3m)

# df_ftm = fetch_pct_stat_data('2021-22', 'FTM')
# print(df_ftm)