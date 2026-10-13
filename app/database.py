import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE = BASE_DIR / "study_planner.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS timetable_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day_index INTEGER NOT NULL,
            day_name TEXT NOT NULL,
            module TEXT NOT NULL,
            assessment TEXT,
            start_minutes INTEGER NOT NULL,
            end_minutes INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    connection.commit()
    connection.close()


def create_user(full_name, email, password):

    connection = get_connection()

    hashed_password = generate_password_hash(password)

    try:

        connection.execute(
            """
            INSERT INTO users (full_name, email, password)
            VALUES (?, ?, ?)
            """,
            (full_name, email, hashed_password)
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def get_user(email):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT * FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    connection.close()

    return user


def verify_password(stored_password, entered_password):

    return check_password_hash(
        stored_password,
        entered_password
    )


def save_timetable(user_id, sessions):
    """
    Saves a student's generated timetable.
    Any earlier timetable for the same student is replaced.
    """

    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM timetable_sessions WHERE user_id = ?",
            (user_id,)
        )

        connection.executemany(
            """
            INSERT INTO timetable_sessions
            (user_id, day_index, day_name, module, assessment,
             start_minutes, end_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    user_id,
                    s["day_index"],
                    s["day_name"],
                    s["module"],
                    s["assessment"],
                    s["start"],
                    s["end"]
                )
                for s in sessions
            ]
        )

        connection.commit()

    finally:
        connection.close()


def get_timetable(user_id):
    """
    Returns all saved study sessions for a student.
    """

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT * FROM timetable_sessions
        WHERE user_id = ?
        ORDER BY day_index, start_minutes
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return rows
