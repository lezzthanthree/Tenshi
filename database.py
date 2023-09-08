import sqlite3

class Database():
    def connect_database():
        return sqlite3.connect("data.db")

    def execute_command(command: str, parameters=()):
        conn = Database.connect_database()
        cursor = conn.cursor()
        cursor.execute(command, parameters)
        conn.commit()
        conn.close()
    
    def get_data(command: str, parameters=()):
        conn = Database.connect_database()
        cursor = conn.cursor()
        cursor.execute(command, parameters)
        rows = cursor.fetchall()
        conn.close()

        return rows

create = {
    'guild': """
                CREATE TABLE IF NOT EXISTS guilds (
                    guild_id       INTEGER PRIMARY KEY,
                    guild_name     TEXT NOT NULL,
                    guild_utc      REAL DEFAULT 0
                );
             """,
    'subject': """
                CREATE TABLE IF NOT EXISTS subjects (
                    subject_id      TEXT NOT NULL PRIMARY KEY,
                    subject_name    TEXT NOT NULL,
                    server_id       INTEGER,
                    FOREIGN KEY (server_id) REFERENCES guilds(guild_id)
                );
               """,
    'schedule': """
                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id      TEXT NOT NULL,
                    schedule_day    TEXT NOT NULL,
                    schedule_start  TEXT NOT NULL,
                    schedule_end    TEXT NOT NULL,
                    server_id       INTEGER,
                    FOREIGN KEY (server_id) REFERENCES guilds(guild_id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
                );
                """
}

insert = {
    'guild': """
                INSERT or IGNORE INTO guilds (
                    guild_id,
                    guild_name
                ) VALUES (?, ?)
             """,
    'subject': """
                INSERT INTO subjects (
                    subject_id,
                    subject_name,
                    server_id
                ) VALUES (?, ?, ?)
               """,
    'schedule': """
                INSERT INTO schedules (
                    subject_id,
                    schedule_day,
                    schedule_start,
                    schedule_end,
                    server_id
                ) VALUES (?, ?, ?, ?, ?)
                """
}

delete = {
    'guild': """
                DELETE FROM guilds
                WHERE guild_id = ?
             """,
    'subject': """
                DELETE FROM subjects
                WHERE subject_id = ?
               """
}

update = {
    'guild': """
                UPDATE guilds
                SET guild_name = ?
                WHERE guild_id = ?
             """,
    'utc': """
            UPDATE guilds
            SET guild_utc = ?
            WHERE guild_id = ?
           """,
    'schedule': """
                UPDATE schedules
                SET schedule_day = ?,
                    schedule_start = ?,
                    schedule_end = ?
                WHERE schedule_id = ?
                """
}

read = {
    'utc': """
            SELECT guild_utc FROM guilds WHERE guild_id = ?
           """,
    'subjects_from_guild': """
                            SELECT * FROM subjects WHERE server_id = ?
                           """,
    'subject_from_code': """
                            SELECT * FROM subjects WHERE subject_id = ? AND server_id = ?
                         """,
    'schedules_from_day': """
                            SELECT schedule_id, subject_name, schedule_start, schedule_end
                            FROM schedules
                            INNER JOIN subjects ON schedules.subject_id = subjects.subject_id
                            WHERE schedule_day = ? AND schedules.server_id = ?
                            ORDER BY schedule_start ASC
                          """,
    'schedule_from_id': """
                        SELECT subject_name, schedule_day, schedule_start, schedule_end
                        FROM schedules 
                        INNER JOIN subjects ON schedules.subject_id = subjects.subject_id
                        WHERE schedule_id = ? AND schedules.server_id = ?
                        """
}