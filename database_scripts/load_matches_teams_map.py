from sqlalchemy import select
from sqlalchemy.orm import sessionmaker



import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from models import Base, engine, matches_to_teams, Match


def populate_matches_to_teams(Base):
    """
    Create map of matches to teams

    :param Base: (sqlalcemy.declarativebase) Base class for declarative base definitions
    :return: (None)
    """
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    select_statement = select([Match.WTeamID.label('TeamID'), Match.id, Match.mdid]).union(
        select([Match.LTeamID.label('TeamID'), Match.id, Match.mdid])).order_by(Match.mdid.desc())

    session.execute(matches_to_teams.insert().from_select(['TeamID', 'id', 'mdid'], select_statement))

    session.commit()
    session.close()


populate_matches_to_teams(Base)
