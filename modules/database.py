__author__ = 'tinglev@kth.se'

import os
import pyodbc

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

def get_player(player_name):
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(f"SELECT PlayerId, Name FROM players WHERE name = '{player_name}'")
        result = cursor.fetchone()
        if result:
            return result
        return None
    finally:
        cnx.close()    

def player_exists(player_name):
    if get_player(player_name):
        return True
    return False

def register_player(player_name):
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO players (Name) VALUES (?)", player_name)
        cursor.commit()
    finally:
        cnx.close()

def register_result(p1_id, p2_id, p1_score, p2_score, date):
    cnx = get_connection()
    try:
        cursor = cnx.cursor()
        cursor.execute(f"INSERT INTO results (Player1Id, Player2Id, Player1Score, Player2Score, PlayedAt) "
                        f"VALUES (?, ?, ?, ?, ?)",
                        p1_id, p2_id, p1_score, p2_score, date)
        cursor.commit()
    finally:
        cnx.close()
