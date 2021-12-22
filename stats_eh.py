from nba_api.stats.endpoints import leagueleaders
import json
import sys
import pandas as pd
import plotly.express as px

"""
- Query user for season
- Query user for stat
	- func to display all stat abbreviations
- Populate df containing all stats for given season
- Sort by leaders of desired stat
- Plot sorted df
"""
season_string = ""
stat_string = ""

def fetch_stat_abbrvs():
	response = leagueleaders.LeagueLeaders()
	stats = json.loads(response.league_leaders.get_json())

	return stats['headers'][4:-1]

def fetch_stat_data(year, stat):
	"""
	Conditional in case response is None?
	- Get stats for a given year
	- Get stats in json form 
	- Populate dataframe containing all stats from given year
	- Return dataframe containing leaders (top30) of desired stat
	"""
	response = leagueleaders.LeagueLeaders(season=year)
	stats = json.loads(response.league_leaders.get_json())

	df_stats = pd.DataFrame(stats['data'], columns=stats['headers'])

	df_stat = df_stats[['PLAYER', stat]].sort_values(by=stat, ascending=False)

	return df_stat[:30]

#print(fetch_stat_data('2020-21', 'AST'))

if __name__ == '__main__':

	# #Set a flag
	# active = True

	while True:

		try:
			season_string = input("\nEnter the NBA Season (e.g: '2015-16' for 2015 Season): ")
			print("\nStat abbreviations: {}".format(fetch_stat_abbrvs()))
			stat_string = (input("\nEnter stat abbreviation (e.g: 'AST' for assists): ")).upper()

			response = fetch_stat_data(season_string, stat_string)
			print(response)
			# print(response.empty)

			if response.empty == False:
				fig = px.bar(response, x='PLAYER', y=[response[stat_string]],
						title='Leaders in {} for the {} regular season'.format(stat_string, season_string),
						labels={'value': stat_string, 'PLAYER': 'Player', 'variable': stat_string},
						)

				fig.update_traces(texttemplate=response[stat_string].to_list(), textposition='inside')
				fig.update_layout(xaxis_tickangle=-45, showlegend=False,
						uniformtext_minsize=8, uniformtext_mode='show'
						)
				fig.show()
			else:
				#TypeError and KeyError need to be addressed (when stat format wrong or params missing)
				print("\nData Error")
				print("Please ensure the season is the same format as e.g: '2015-16'")
				continue

			#Flag for repeat
			repeat_active = True
			while repeat_active:
				repeat = input("\nWould you like to visualise another stat? (Y/N): ")

				if repeat.upper() == 'N':
					print("\nExiting program...")
					sys.exit()
				elif repeat.upper() == 'Y':
					repeat_active = False
					print("\nStarting another visualisation...")
				else:
					print("\nPlease provide your answer with either Y or N")
					continue

		except json.decoder.JSONDecodeError as jerr:
			print("\nJSONDecoderError: ", jerr)
			print("Please ensure the season is the same format as e.g: '2015-16'")

		except KeyError as kerr:
			print("\nKeyError: ", kerr)
			print("Please ensure that the stat is in the same format as e.g: 'AST'")

		# except TypeError as terr:
		# 	print("\nTypeError: ", terr)
		# 	print("Please ensure that a season AND a stat are provided (no empty inputs)")

		# except Exception as e:
		# 	print("Error")
		# 	print(e)

