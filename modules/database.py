__author__ = 'tinglev@kth.se'

import os
import pyodbc
from modules import slack

def get_connection():
    return pyodbc.connect(os.environ.get('CONNECTION_STRING'))

def init():
    cnx = get_connection()
    cnx.close()
    return True

def run_select(query):
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cnx.close()

def get_player(slack_mention):
    if not slack_mention:
        return None
    slack_user_id = slack.mention_to_user_id(slack_mention)
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT PlayerId, Name, SlackUserId "
            "FROM players WHERE SlackUserId = ?",
            slack_user_id
        )
        result = cursor.fetchone()
        if result:
            return result
        return None
    finally:
        cnx.close()

def get_all_players():
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT PlayerId, Name, SlackUserId FROM players"
        )
        result = cursor.fetchall()
        if result:
            return result
        return None
    finally:
        cnx.close()

def get_last_5_results():
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "select top 5 p1.name as p1_name, p2.name as p2_name, "
            "r.player1score as p1_score, r.player2score as p2_score, "
            "r.playedat as playedat "
            "from results as r "
            "join players as p1 on r.player1id = p1.playerid "
            "join players as p2 on r.player2id = p2.playerid "
            "order by playedat desc"
        )
        result = cursor.fetchall()
        if result:
            return result
        return None
    finally:
        cnx.close()

def get_leaderboard():
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "select 0 as score, p.name as name, count(*) as games, "
            "(isnull((select count(*) from results where p.playerid = player1id and player1score > player2score group by player1id), 0) + "
            "isnull((select count(*) from results where p.playerid = player2id and player2score > player1score group by player2id), 0)) as wins, "
            "(isnull((select sum(player1score) from results where p.playerid = player1id group by player1id), 0) + "
            "isnull((select sum(player2score) from results where p.playerid = player2id group by player2id), 0)) as wonpoints, "
            "(isnull((select sum(player1score) from results where p.playerid = player2id group by player2id), 0) + "
            "isnull((select sum(player2score) from results where p.playerid = player1id group by player1id), 0)) as lostpoints "
            "from players as p "
            "join results as r on p.playerid = r.player1id or p.playerid = r.player2id "
            "group by p.name, p.playerid"
        )
        results = cursor.fetchall()
        if results:
            for result in results:
                result.score = result.wins + (result.games - result.wins) * -0.5
            results.sort(key=lambda result: result.score, reverse=True)
            return results
        return None
    finally:
        cnx.close()

def player_exists(slack_mention):
    return True if get_player(slack_mention) else False

def register_player(slack_user_id):
    cnx = get_connection()
    player_name = ''
    try:
        user_info = slack.get_user_info(slack_user_id)
        player_name = user_info['user']['real_name']
        cursor = cnx.cursor()
        cursor.execute(
            "INSERT INTO players (Name, SlackUserId) VALUES (?, ?)",
            player_name, slack_user_id
        )
        cursor.commit()
    finally:
        cnx.close()
    return player_name

def register_result(p1_id, p2_id, p1_score, p2_score, date):
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO results (Player1Id, Player2Id, Player1Score, "
                       "Player2Score, PlayedAt) VALUES (?, ?, ?, ?, ?)",
                       p1_id, p2_id, p1_score, p2_score, date)
        cursor.commit()
    finally:
        cnx.close()
