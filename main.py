from __future__ import annotations

import contextlib
import dataclasses
import sqlite3
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Generator

db: sqlite3.Connection | None = None


@contextlib.contextmanager
def database_context(db: sqlite3.Connection) -> Generator[sqlite3.Cursor, None, None]:
    """Database cursor context manager.

    The cursor is closed and can no longer process statements after
    this context exits.

    :param db: Database connection.
    :yield: A cursor to the database.
    :return: None.
    """
    cursor = db.cursor()
    yield cursor
    cursor.close()


@dataclasses.dataclass(slots=True)
class VideoGameModel:
    """Video Game Object."""
    name: str
    rating: float
    _id: int | None = None

    @property
    def id(self) -> int | None:
        """Property getter: id."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Property setter: id."""
        if not isinstance(value, int):
            raise ValueError
        self._id = value


def create_video_game_table(db: sqlite3.Connection) -> None:
    """Create the video game table.

    :param db: Database connection.
    :return: None.
    """
    with  database_context(db) as cursor:
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS videogames(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       rating REAL NOT NULL,
                       CONSTRAINT unique_videogame_name UNIQUE(name) ON CONFLICT ROLLBACK
                       )""")


def add_video_game(db: sqlite3.Connection, video_game: VideoGameModel) -> None:
    """Add a new video game to the database.

    :param db: Database connection.
    :param video_game: The video game to add to the database.
    :return: None.
    """
    with database_context(db) as cursor:
        cursor.execute("""
                       INSERT INTO videogames(name, rating)
                       VALUES(?, ?)
                       """,
                       (video_game.name, video_game.rating))
        video_game.id = cursor.lastrowid


def get_all_video_games(db: sqlite3.Connection) -> list[VideoGameModel]:
    """Get all video games from database.

    :param db: Database connection.
    :return: A list of VideoGameModel objects from the database.
    """
    with database_context(db) as cursor:
        cursor.execute("""SELECT name, rating, id FROM videogames""")

        video_games: list[VideoGameModel] = []
        for row in cursor.fetchall():
            video_games.append(VideoGameModel(*row))

    return video_games


def get_video_game_by_name(db: sqlite3.Connection, name: str) -> VideoGameModel:
    """Get a single video game from the database.

    The database is queried based on the name of the video game.

    :param db: Database connection.
    :param name: Name of video game to retrieve from database.
    :return: A VideoGameModel object from the database.
    """
    with database_context(db) as cursor:
        cursor.execute("""SELECT name, rating, id FROM videogames WHERE name = ?""",
                       (name,))
        return VideoGameModel(*cursor.fetchone())


def delete_video_game_by_id(db: sqlite3.Connection, id: int) -> None:
    """Delete a video game from the database.

    The database is queried base on the database id of the video game.

    :param db: Database connection.
    :param id: Database id of the video game to delete.
    :return: None.
    """
    with database_context(db) as cursor:
        cursor.execute("""DELETE FROM videogames WHERE id = ?""", (id,))


def main():
    create_video_game_table(db)

    satisfactory = VideoGameModel(name="Satisfactory", rating="90")
    print(f"Before adding to database: {satisfactory=}")
    add_video_game(db, satisfactory)
    print(f"After adding to database: {satisfactory=}")

    games = get_all_video_games(db)
    print(f"Retrieved games from database: {games=}")

    satisfactory = get_video_game_by_name(db, "Satisfactory")
    print(f"Retrieved single game from database: {satisfactory=}")

    delete_video_game_by_id(db, satisfactory.id)
    games = get_all_video_games(db)
    print(f"Games after deleting Satisfactory: {games=}")


if __name__ == "__main__":
    try:
        db = sqlite3.connect(":memory:", check_same_thread=False)
        main()
    finally:
        if isinstance(db, sqlite3.Connection):
            db.close()
