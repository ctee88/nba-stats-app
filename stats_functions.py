from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.endpoints import leaguestandings
import plotly.subplots as sp
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

stats_dict = {
	"stat_types": ['SHOOTING', 'NON-SHOOTING', 'STANDINGS'],
	"shooting_stats": ['FGM', 'FG3M', 'FTM'],
	"non_shooting_stats": ['GP', 'MIN', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS', 'AST_TOV', 'STL_TOV'],
	"standings_stats": ['TeamName', 'Conference', 'PlayoffRank', 'WINS', 'LOSSES', 'WinPCT', 'Record', 'L10'],
}

def show_shooting_stats():
	print("\nShooting stats available: {}".format(stats_dict['shooting_stats']))

def show_non_shooting_stats():
	print("\nNon-shooting stats available: {}".format(stats_dict['non_shooting_stats']))

#HELPER FUNCTION - RETURNS DF WITH ALL STATS FOR GIVEN YEAR
def fetch_stats(year):
	stats = json.loads(leagueleaders.LeagueLeaders(season=year).league_leaders.get_json())
	df = pd.DataFrame(stats['data'], columns=stats['headers'])

	return df

#FETCH SPECIFIC NON-SHOOTING STAT DATA
def fetch_non_shooting_stat(year, stat):
	df_stats = fetch_stats(year)
	df_stat = df_stats[['PLAYER', stat, 'GP', 'MIN']].sort_values(by=stat, ascending=False)

	return df_stat[:30]

#FETCH SPECIFIC SHOOTING STAT DATA
def fetch_shooting_stat(year, stat):
	df_stats = fetch_stats(year)

	if stat == 'FGM':
		df_fgm = df_stats[
			['PLAYER', stat, 'FGA', 'FG_PCT']
			].sort_values(by=stat, ascending=False)
		return df_fgm[:30]

	elif stat == 'FG3M':
		df_fg3m = df_stats[
			['PLAYER', stat, 'FG3A', 'FG3_PCT']
			].sort_values(by=stat, ascending=False)
		return df_fg3m[:30]

	elif stat == 'FTM':
		df_ftm = df_stats[
			['PLAYER', stat, 'FTA', 'FT_PCT']
			].sort_values(by=stat, ascending=False)
		return df_ftm[:30]

#FETCH STANDINGS DATA FOR SPECIFIC YEAR
def fetch_standings(year):
	standings = json.loads(leaguestandings.LeagueStandings(season=year).standings.get_json())
	df = pd.DataFrame(standings['data'], columns=standings['headers'])

	df_standings = df[stats_dict['standings_stats']]

	team_names = {}
	team_names['Team Names'] = []

	for teams_data in standings['data']:
		#[3] = City Names, [4] = Team Names. Join for full team name.
		city_and_team = [teams_data[3], teams_data[4]]
		team_name = " ".join(city_and_team)
		team_names['Team Names'].append(team_name)
	
	#Replace short team name with full team name in df_standings.
	df_teamnames = pd.DataFrame(team_names)
	df_standings = df_standings.assign(TeamName=df_teamnames['Team Names'])

	#Return 2 dfs: one for East conf, one for West conf.
	df_east = df_standings[df_standings['Conference']=='East']
	df_west = df_standings[df_standings['Conference']=='West']
	
	return df_east, df_west
	
#GRAPH FOR NON-SHOOTING STATS (BAR CHART)
def plot_non_shooting_stat(df, year, stat):
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

#GRAPH FOR SHOOTING STATS
def plot_shooting_stat(df, year):
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

	fig = sp.make_subplots(specs=[[{"secondary_y": True}]])
	
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
		customdata=pct_array,
		hovertemplate="<br>".join([
			"Player: %{x}",
			"<b>Attempted: %{y}</b>",
			"<b>%: %{customdata[0]:.3f}</b>",
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

#GRAPH FOR STANDINGS (STACKED HORIZONTAL BARS)
def plot_standings(dfs, year):
	#Create figs for East and West
	fig_east = px.bar(dfs[0], x=['WINS', 'LOSSES'], y='TeamName',
		custom_data=[dfs[0]['Record'], dfs[0]['WinPCT'], dfs[0]['L10']],
		orientation='h'
		)

	fig_west = px.bar(dfs[1], x=['WINS', 'LOSSES'], y='TeamName',
		custom_data=[dfs[1]['Record'], dfs[1]['WinPCT'], dfs[1]['L10']],
		orientation='h'
		)

	#Store traces from each plot in an array
	fig_east_traces, fig_west_traces = [], []

	for trace in range(len(fig_east['data'])):
		fig_east_traces.append(fig_east['data'][trace])
	for trace in range(len(fig_west['data'])):
		fig_west_traces.append(fig_west['data'][trace])

	#Create 2x1 subplot which the traces will be added to
	final_fig = sp.make_subplots(rows=2, cols=1,
		subplot_titles=('Eastern Conference', 'Western Conference')
		)

	#Add traces to final plot within the subplot.
	for traces in fig_east_traces:
		final_fig.append_trace(traces, row=1, col=1)
	for traces in fig_west_traces:
		final_fig.append_trace(traces, row=2, col=1)

	final_fig.update_layout(
		barmode='stack', xaxis_tickangle=-45,
		xaxis2_tickangle=-45, 
		title_text='NBA Standings for the {} regular season'.format(year),
		showlegend=False
		)

	final_fig.update_xaxes(title_text='Number of Wins/Losses')
	final_fig.update_yaxes(title_text='Teams')

	final_fig.update_traces(marker_line_color='rgb(8,48,107)',
		hovertemplate="<br>".join([
			"Team: %{y}",
			"<b>Amount: %{x}</b>",
			"<b>Record (W-L): %{customdata[0]}</b>",
			"<b>Win %: %{customdata[1]}</b>",
			"<b>L10 (W-L): %{customdata[2]}</b>",
		])
	)

	final_fig.show()
