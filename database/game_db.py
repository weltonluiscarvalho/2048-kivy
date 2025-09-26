import os
import uuid
import sqlite3
from datetime import datetime
from math import ceil
from kivy.app import App

DB_NAME = 'game.db'
CONN = None
CURSOR = None
DB_DIR = ''
DB_PATH = ''

def open_connection():
    global DB_DIR, DB_PATH, CONN, CURSOR
    app = App.get_running_app()
    DB_DIR = app.user_data_dir if app else "" 
    DB_PATH = os.path.join(DB_DIR, DB_NAME)
    CONN = sqlite3.connect(DB_PATH)
    CURSOR = CONN.cursor()

def close_connection():
    global CONN, CURSOR
    if CONN and CURSOR:
        CURSOR.close()
    if CONN:
        CONN.close()

def select_pieces_move_from_move(game_id, move_number):
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    res = CURSOR.execute(
         '''
         SELECT final_value, initial_position_id, final_position_id, performed_merge FROM PIECE_MOVE WHERE game_id = ? and move_number = ?
         ''', (game_id, move_number)
    )

    piece_moves = res.fetchall()

    if not piece_moves:
        return None

    moves = []
    for piece_move in piece_moves:

        initial_position = CURSOR.execute(
             '''
             SELECT row, column FROM POSITION WHERE position_id = ?
             ''', (piece_move[1],)
        )

        initial_row, initial_column = initial_position.fetchone()
        
        final_position = CURSOR.execute(
             '''
             SELECT row, column FROM POSITION WHERE position_id = ?
             ''', (piece_move[2],)
        )

        final_row, final_column = final_position.fetchone()

        moves.append({
            "final_value": piece_move[0],
            "initial_position": {
                "row": initial_row,
                "column": initial_column
            },
            "final_position": {
                "row": final_row,
                "column": final_column
            },
            "is_merge": piece_move[3]
        })


    print(moves)
    return moves


def select_last_do_move(game_id, type_number):
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    res = CURSOR.execute(
         '''
         SELECT move_number, direction, piece_position_id FROM MOVE WHERE game_id = ? and type_number = ? and type = ? ORDER BY move_number DESC
         ''', (game_id, type_number, "do")
    )

    res = res.fetchone()
    if not res:
        return None

    move_number, direction, new_piece_position = res

    res = CURSOR.execute(
         '''
         SELECT row, column FROM POSITION WHERE position_id = ?
         ''', (new_piece_position,)
    )

    row, column = res.fetchone()

    return {
        "move_number": move_number,
        "direction": direction,
        "row": row,
        "column": column
    }
    

def insert_board(game_id, row, column, value):
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    res = CURSOR.execute(
         '''
         SELECT position_id FROM POSITION WHERE row = ? and column = ?
         ''', (row, column)
    )

    position_id = res.fetchone()[0]

    CURSOR.execute(
        '''
        INSERT INTO BOARD (game_id, position_id, value)
        VALUES (?, ?, ?)
        ''', (game_id, position_id, value)
    )

    CONN.commit()


def insert_piece_move(move_number, game_id, initial_row, initial_column, final_row, final_column, final_value, merge):
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    res = CURSOR.execute(
         '''
         SELECT position_id FROM POSITION WHERE row = ? and column = ?
         ''', (initial_row, initial_column)
    )

    initial_position_id = res.fetchone()[0]

    res = CURSOR.execute(
         '''
         SELECT position_id FROM POSITION WHERE row = ? and column = ?
         ''', (final_row, final_column)
    )

    final_position_id = res.fetchone()[0]

    CURSOR.execute(
        '''
        INSERT INTO PIECE_MOVE (move_number, game_id, initial_position_id, final_position_id, final_value, performed_merge)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (move_number, game_id, initial_position_id, final_position_id, final_value, merge)
    )

    CONN.commit()


def insert_move(move_number, game_id, move_type, direction, type_number, score, piece_row, piece_column):
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    res = CURSOR.execute(
         '''
         SELECT position_id FROM POSITION WHERE row = ? and column = ?
         ''', (piece_row, piece_column)
    )

    position_id = res.fetchone()[0]

    CURSOR.execute(
        '''
        INSERT INTO MOVE (move_number, game_id, type, direction, type_number, score, piece_position_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (move_number, game_id, move_type, direction, type_number, score, position_id)
    )

    CONN.commit()


def populate_position():
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    res = CURSOR.execute(
         '''
         SELECT * FROM POSITION
         '''
    )

    if res.fetchone():
        return

    data = []
    
    position = 1
    for row in range(4):
        for column in range(4):
            data.append((position, row, column))
            position += 1

    CURSOR.executemany(
         ''' INSERT INTO POSITION (position_id, row, column)
         VALUES (?, ?, ?)
         ''', data
    )
    CONN.commit()


def insert_game():
    game_id = str(uuid.uuid4())
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    CURSOR.execute(
         '''
         INSERT INTO GAME (game_id, final_score, initial_date_timestamp, final_date_timestamp)
         VALUES (?, ?, ?, ?)
         ''', (game_id, 0, ceil(int(datetime.now().timestamp())), ceil(int(datetime.now().timestamp())))
    )
    CONN.commit()

    return game_id


def create_tables():
    global CONN, CURSOR

    if not CONN and not CURSOR:
        open_connection()

    CURSOR.execute(
        "CREATE TABLE IF NOT EXISTS POSITION (\
        position_id INTEGER PRIMARY KEY,\
        row INTEGER,\
        column INTEGER\
        )"
    )

    CURSOR.execute(
        "CREATE TABLE IF NOT EXISTS GAME (\
        game_id TEXT PRIMARY KEY,\
        final_score INTEGER,\
        initial_date_timestamp INTEGER,\
        final_date_timestamp INTEGER\
        )"
    )

    CURSOR.execute(
        "CREATE TABLE IF NOT EXISTS MOVE (\
        move_number INTEGER,\
        game_id TEXT REFERENCES GAME(game_id),\
        type TEXT,\
        direction TEXT,\
        type_number INTEGER,\
        score INTEGER,\
        piece_position_id INTEGER REFERENCES POSITION(position_id),\
        PRIMARY KEY (move_number, game_id)\
        )"
    )

    CURSOR.execute(
        "CREATE TABLE IF NOT EXISTS PIECE_MOVE (\
        move_number INTEGER REFERENCES MOVE(move_number),\
        game_id TEXT REFERENCES GAME(game_id),\
        initial_position_id INTEGER REFERENCES POSITION(position_id),\
        final_position_id INTEGER REFERENCES POSITION(position_id),\
        final_value INTEGER,\
        performed_merge INTEGER,\
        PRIMARY KEY (move_number, game_id, initial_position_id, final_position_id)\
        )"
    )

    CURSOR.execute(
        "CREATE TABLE IF NOT EXISTS BOARD (\
        game_id TEXT REFERENCES GAME(game_id),\
        position_id INTEGER REFERENCES POSITION(position_id),\
        value INTEGER,\
        PRIMARY KEY (game_id, position_id)\
        )"
    )

