__author__ = 'tinglev@kth.se'

import os
import logging
import datetime
import pyodbc
from modules import slack

def get_connection():
    return pyodbc.connect(os.environ.get('CONNECTION_STRING'))

def init():
    cnx = get_connection()
    cnx.close()
    return True

def fetchall(cursor):
    return cursor.fetchall()

def fetchone(cursor):
    return cursor.fetchone()

def run_select(query, *params, fetch_func=fetchall):
    log = logging.getLogger(__name__)
    log.debug('Running select with params "%s"', params)
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, params)
        result = fetch_func(cursor)
        if result:
            return result
        return None
    finally:
        cnx.close()

def run_commit(query, *params):
    log = logging.getLogger(__name__)
    log.debug('Running commit with params "%s"', params)
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(query, params)
        cursor.commit()
    finally:
        cnx.close()

def get_latest_result():
    return run_select(
        "SELECT TOP 1 resultid FROM results ORDER BY playedat DESC",
        fetch_func=fetchone
    )

def delete_result(resultid):
    run_commit(
        "DELETE FROM results WHERE resultid = ?",
        resultid
    )

def get_player(slack_mention):
    if not slack_mention:
        return None
    slack_user_id = slack.mention_to_user_id(slack_mention)
    return run_select(
        "SELECT playerid, name, slackuserid "
        "FROM players WHERE slackuserid = ?",
        slack_user_id,
        fetch_func=fetchone
    )

def get_all_players():
    return run_select(
        "SELECT playerid, name, slackuserid FROM players"
    )

# Returns tuple with (result, None) on success and (None, errortext) on error
def get_last_5_results():
    current_season = get_current_season()
    if not current_season:
        return (None, 'There is no active season')
    results = run_select(
        "SELECT TOP 5 p1.name AS p1_name, p2.name AS p2_name, "
        "r.player1score AS p1_score, r.player2score AS p2_score, "
        "r.playedat AS playedat "
        "FROM results AS r "
        "JOIN players AS p1 ON r.player1id = p1.playerid "
        "JOIN players AS p2 ON r.player2id = p2.playerid "
        "WHERE r.seasonid = ? "
        "ORDER BY playedat DESC",
        current_season.seasonid
    )
    if not results:
        return (None, 'Not enough data')
    return (results, None)

def get_season_id(season_name):
    results = run_select(
        "SELECT seasonid "
        "FROM seasons "
        "WHERE name = ?",
        season_name,
        fetch_func=fetchone
    )
    if not results:
        return None
    return results.seasonid

def get_all_seasons():
    return run_select(
        "SELECT name, startedat, endedat "
        "FROM seasons"
    )

# Returns tuple with (result, None) on success and (None, errortext) on error
def get_leaderboard(season_name=None):
    if not season_name:
        # Get current leaderboard
        current_season = get_current_season()
        if not current_season:
            return (None, 'There is no active season')
        season_id = current_season.seasonid
    else:
        # Get an old season leaderboard
        season_id = get_season_id(season_name)
        if not season_id:
            return (None, 'No season with that name')
    results = run_select(
        "SELECT p.imageurl as image_url, p.slackuserid as slack_user_id, s.name as season, 0 AS score, p.name AS player_name, COUNT(*) AS games, "
        "(ISNULL((SELECT COUNT(*) FROM results WHERE seasonid = ? AND p.playerid = player1id AND player1score > player2score GROUP BY player1id), 0) + "
        "   ISNULL((SELECT COUNT(*) FROM results WHERE seasonid = ? AND p.playerid = player2id AND player2score > player1score GROUP BY player2id), 0)) AS wins, "
        "(ISNULL((SELECT sum(player1score) FROM results WHERE seasonid = ? AND p.playerid = player1id GROUP BY player1id), 0) + "
        "   ISNULL((SELECT sum(player2score) FROM results WHERE seasonid = ? AND p.playerid = player2id GROUP BY player2id), 0)) AS wonpoints, "
        "(ISNULL((SELECT sum(player1score) FROM results WHERE seasonid = ? AND p.playerid = player2id GROUP BY player2id), 0) + "
        "   ISNULL((SELECT sum(player2score) FROM results WHERE seasonid = ? AND p.playerid = player1id GROUP BY player1id), 0)) AS lostpoints "
        "FROM players AS p "
        "JOIN results AS r ON p.playerid = r.player1id OR p.playerid = r.player2id "
        "JOIN seasons AS s ON s.seasonid = ? "
        "WHERE r.seasonid = ? "
        "GROUP BY p.imageurl, p.slackuserid, s.name, p.name, p.playerid",
        season_id, season_id, season_id,
        season_id, season_id, season_id,
        season_id, season_id
    )
    if results:
        for result in results:
            result.score = result.wins + (result.games - result.wins) * -0.5
        results.sort(key=lambda result: result.score, reverse=True)
        return (results, None)
    return (None, 'Not enough data')

def player_exists(slack_mention):
    return True if get_player(slack_mention) else False

def register_player(slack_client, slack_user_id):
    user_info = slack.get_user_info(slack_client, slack_user_id)
    image_url = slack.get_user_image_url(user_info)
    player_name = user_info['user']['real_name']
    run_commit(
        "INSERT INTO players (name, slackuserid, imageurl) VALUES (?, ?, ?)",
        player_name, slack_user_id, image_url
    )
    return player_name

def create_new_season(season_name):
    current_season = get_current_season()
    if current_season:
        # End the current season
        run_commit(
            "UPDATE seasons SET endedat = ? WHERE seasonid = ?",
            datetime.datetime.now(), current_season.seasonid
        )
    run_commit(
        "INSERT INTO seasons (name, startedat) VALUES (?, ?)",
        season_name, datetime.datetime.now()
    )

def get_current_season():
    return run_select(
        "SELECT seasonid, name, startedat, endedat FROM seasons "
        "WHERE endedat IS NULL",
        fetch_func=fetchone
    )

# Returns error text on error, else None
def register_result(p1_id, p2_id, p1_score, p2_score, date):
    current_season = get_current_season()
    if not current_season:
        return 'There is no active season'
    run_commit(
        "INSERT INTO results (player1id, player2id, player1score, "
        "player2score, playedat, seasonid) VALUES (?, ?, ?, ?, ?, ?)",
        p1_id, p2_id, p1_score, p2_score, date, current_season.seasonid
    )
    return None

def drop_and_create_tables():
    run_commit(
        "DROP TABLE IF EXISTS results"
    )
    run_commit(
        "DROP TABLE IF EXISTS players"
    )
    run_commit(
        "DROP TABLE IF EXISTS seasons"
    )
    run_commit(
        "CREATE TABLE players ("
        "playerid INT IDENTITY(1,1) PRIMARY KEY, "
        "name VARCHAR(50) NOT NULL, "
        "slackuserid VARCHAR(15) NOT NULL, "
        "imageurl VARCHAR(200) NULL"
        ")"
    )
    run_commit(
        "CREATE TABLE seasons ("
        "seasonid INT IDENTITY(1,1) PRIMARY KEY, "
        "name VARCHAR(100) NOT NULL, "
        "startedat DATETIME NOT NULL, "
        "endedat DATETIME NULL, "
        ")"
    )
    run_commit(
        "CREATE TABLE results ("
        "resultid INT IDENTITY(1,1) PRIMARY KEY, "
        "player1id int FOREIGN KEY REFERENCES players(playerid), "
        "player2id int FOREIGN KEY REFERENCES players(playerid), "
        "player1score int NOT NULL, "
        "player2score int NOT NULL, "
        "playedat DATETIME NOT NULL, "
        "seasonid int FOREIGN KEY REFERENCES seasons(seasonid)"
        ")"
    )
