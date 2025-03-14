from sqlalchemy.orm import sessionmaker


import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from elo_run.TeamMatchStack import TeamMatchStack


from models import engine, Team


Session = sessionmaker(bind=engine)
session = Session()
teamids = [teamid for teamid, in session.query(Team.TeamID)]
session.close()

team_stacks = {}

for TeamID in teamids:
    print(TeamID)
    team_stack = TeamMatchStack(TeamID)
    team_stack.update_match_stats()

    team_stacks[TeamID] = team_stack

