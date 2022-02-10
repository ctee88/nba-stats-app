import stats_functions as sf
import re
import sys
import json

def run_app():
	while True:
		try:
			season_string = input("\nEnter the NBA Season (e.g: '2015-16' for 2015 Season): ")

			if not re.match('^(\d{4}-\d{2})?$', season_string) or not season_string:
				print("Please enter a valid season (see e.g in brackets)")
				continue
		
			"""
			-Check whether returned df is empty
			-Year outside of range (e.g 2050-51) or incorrect input (e.g 2021-20) will return empty df
			-This also covers the standings API call: Different endpoint to stats endpoint but passing the
			same parameter (season).
			"""
			df_stats = sf.fetch_stats(season_string)
			if df_stats.empty == True:
				print("Please enter a valid season (see e.g in brackets)")
				continue

			stat_type_string = None
			while stat_type_string is None:
				stat_type_string = input("\nEnter type of stat from 'Shooting', 'Non-shooting', 'Standings':").upper()
				#Only exits loop once user provides a valid stat-type.
				if stat_type_string not in sf.stats_dict['stat_types']:
					print("Please enter a valid stat type ('Shooting', 'Non-shooting', 'Standings')")
					stat_type_string = None

			if stat_type_string == 'SHOOTING':
				sf.show_shooting_stats()

				stat_string = None
				while stat_string is None:
					stat_string = input(("\nEnter shooting stat abbreviation (e.g: FG3M for 3-point shots): ")).upper()

					if stat_string in sf.stats_dict['shooting_stats']:
						df = sf.fetch_shooting_stat(season_string, stat_string)
						sf.plot_shooting_stat(df, season_string)
					else:
						print("Please enter a valid shooting stat")
						stat_string = None

			elif stat_type_string == 'NON-SHOOTING':
				sf.show_non_shooting_stats()

				stat_string = None
				while stat_string is None:
					stat_string = input(("\nEnter non-shooting stat abbreviation (e.g: AST): ")).upper()

					if stat_string in sf.stats_dict['non_shooting_stats']:
						df = sf.fetch_non_shooting_stat(season_string, stat_string)
						sf.plot_non_shooting_stat(df, season_string, stat_string)
					else:
						print("Please enter a valid non-shooting stat")
						stat_string = None

			elif stat_type_string == 'STANDINGS':
				dfs = sf.fetch_standings(season_string)
				sf.plot_standings(dfs, season_string)

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

		except EOFError as eoferr:
			print("\nEOFError: ", eoferr)
			print("Please ensure your inputs match the examples in brackets")

if __name__ == '__main__':
	run_app()
