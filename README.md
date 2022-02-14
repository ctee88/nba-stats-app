# nba-stats-app
A program with user functionality where the user can look at some basic visualisations (player stats or team standings). The program uses the nba_api API client package (see https://github.com/swar/nba_api) to access the APIs for NBA.com. There is extensive documentation found on this repository, thank you for all of your hard work! This project would not be possible without this amazing repository.

# Features
- User can provide a season, type of stat (**shooting/non-shooting/standings**) and stat (e.g. **Shooting: Field Goals Made (FGM). Non-shooting: Blocks (BLK)**)
- A graph is then plotted corresponding to the user input:

  - Shooting stats will return a grouped-bar graph of the top 30 players (for a specific season) who have **Made** the most of a type of shot, their **Attempts** of said shot and the respective **Percentage** is included in the hovertext of each bar. ![]()
  
  - Non-shooting stats will return a bar graph of the top 30 players (for a specific season) for a specific **Stat**. Players' **Minutes Played** and **Games Played** are    included in the hovertext of each bar. ![]()

  - Standings stats will return two stacked-bar graphs representing the **Wins** and **Losses** of the teams in the different conferences (East and West). Teams' overall **W-L Record, Win %, Last 10 games record** are included in the hovertext of each bar. ![]()
  
   **Note: Graph may appear squashed on smaller screens, zoom-out accordingly (*CTRL* and *-* key on Windows).**

# Requirements
- Python 3.8 (or newer)
- Libraries: 
  - nba_api
  - requests (nba_api uses requests to make the API calls)
  - plotly
  - pandas
  - numpy

# Installation
### Python 3.8
- See https://www.codecademy.com/article/install-python for python 3.8 installation instructions.

### Libraries
- Once Python has been installed, run the command prompt (cmd) and enter:
```
python -m pip install nba_api

python -m pip install requests 

python -m pip install plotly

python -m pip install pandas

python -m pip install numpy (may already be installed during Python installation)
```

# Usage
## Running the program
1. Access the directory of the nba-stats-app file through the command prompt:
```
cd [File Path]
```
2. Then enter:
```
python main.py
```
3. The program will prompt the user for their input at different stages. Instructions are provided within the program to ensure that the user enters the correct input (see examples in brackets when the program is running).

## Exiting the program
You can exit the program by inputting 'N' when prompted at the end of a visualisation. (See limitations)

# Components
See the relevant files for more detailed annotations. My project is made up of these parts:

- main.py - Executable code to run the game is located here. Control flow is managed in this file.
- stats_functions.py - Module containing all of the functions used to make the API calls, process the data and create the visualisations.

# Limitations
- For shooting stats, the program only retrieves the top 30 players of shots **made** and not **attempted** - Can't fetch the top 30 players who have **attempted** the most of a certain type of shot.
- Shooting stats graph scaling or graph type (bar graph) may be an issue as it is difficult to see the difference in shots made with adjacent players on the visualisation.
 
**Features to be added:**
- Will need to add a feature which allows the user to exit the program at any point instead of just at the end.
- Hovertext for shooting and non-shooting stats could include a few more useful metrics: 
  - Shooting: **Games Played, Minutes Played, Team Name**
  - Non-shooting: **Team Name**
- Need to allow the user to input a season type: **Regular** or **Play-offs** (currently regular by default)
