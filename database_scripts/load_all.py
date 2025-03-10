import pandas as pd
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from models import Base, engine, Match, Team

DATA_PATH = os.environ["DATA_PATH"]
DATA_PREFIX = os.environ["DATA_PREFIX"]


def _add_match_id(df):
    # Create match id for searching
    lowest_id = df.loc[:, ["WTeamID", "LTeamID"]].min(axis=1)
    highest_id = df.loc[:, ["WTeamID", "LTeamID"]].max(axis=1)
    df["MatchID"] = lowest_id * 100_000 + highest_id


def load_matches():
    """
    Load matches from data into sqlite database

    :return: (None)
    """
    # Add Tourney Results
    Base.metadata.create_all(engine)
    file_name = f"{DATA_PATH}/{DATA_PREFIX}NCAATourneyDetailedResults.csv"
    df = pd.read_csv(file_name)
    df["stage"] = "T"

    # Create id containing season and day in season as a proxy for date overall
    df["mdid"] = df["Season"] * 1000 + df["DayNum"]
    _add_match_id(df)
    df["WFGP"] = df.WFGM / df.WFGA
    df["WFGP3"] = df.WFGM3 / df.WFGA3
    df["WR"] = df.WOR + df.WDR
    df["LFGP"] = df.LFGM / df.LFGA
    df["LFGP3"] = df.LFGM3 / df.LFGA3
    df["LR"] = df.LOR + df.LDR

    # Add Regular season Results
    file_name = f"{DATA_PATH}/{DATA_PREFIX}RegularSeasonDetailedResults.csv"
    df2 = pd.read_csv(file_name)
    df2["stage"] = "R"
    df2["mdid"] = df2["Season"] * 1000 + df2["DayNum"]
    _add_match_id(df2)
    df2["WFGP"] = df2.WFGM / df2.WFGA
    df2["WFGP3"] = df2.WFGM3 / df2.WFGA3
    df2["WR"] = df2.WOR + df2.WDR
    df2["LFGP"] = df2.LFGM / df2.LFGA
    df2["LFGP3"] = df2.LFGM3 / df2.LFGA3
    df2["LR"] = df2.LOR + df2.LDR

    # Add Secondary Tourney Results
    if DATA_PATH == "M":
        file_name = f"{DATA_PATH}/{DATA_PREFIX}SecondaryTourneyCompactResults.csv"
        df3 = pd.read_csv(file_name)
        df3["stage"] = "S"
        _add_match_id(df3)
        df3.drop("SecondaryTourney", axis=1, inplace=True)
        df3["mdid"] = df3["Season"] * 1000 + df3["DayNum"]

    else:
        df3 = pd.DataFrame()

    df_final = pd.concat([df, df2, df3], ignore_index=True)
    df_final.sort_values(by="mdid", inplace=True)
    df_final.reset_index(drop=True, inplace=True)

    with engine.connect() as connection:
        df_final.to_sql(
            con=connection.connection, index_label="id", name=Match.__tablename__, if_exists="replace"
        )


def load_teams():
    """
    Add teams to database

    :return: (None)
    """
    # Add Teams
    Base.metadata.create_all(engine)
    file_name = f"{DATA_PATH}/{DATA_PREFIX}Teams.csv"
    df = pd.read_csv(file_name, index_col="TeamID")

    # Add in First/Last season columns for womens as they dont exist
    for column in ['FirstD1Season', 'LastD1Season']:
        if column not in df:
            df[column] = None

    with engine.connect() as connection:
        df.to_sql(
            con=connection.connection, index_label="TeamID", name=Team.__tablename__, if_exists="replace"
        )


load_teams()
load_matches()
