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
            subject_privacy INTEGER DEFAULT TRUE,
            ownership_id    INTEGER NOT NULL,
            FOREIGN KEY (ownership_id) REFERENCES guilds(guild_id)
        );
    """,

    'enrollment' : """
        CREATE TABLE IF NOT EXISTS enrollments (
            guild_id        INTEGER NOT NULL,
            subject_id      TEXT NOT NULL,
            PRIMARY KEY (guild_id, subject_id),
            FOREIGN KEY (guild_id) REFERENCES guilds(guild_id),
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
    """,

    'schedule': """
        CREATE TABLE IF NOT EXISTS schedules (
            schedule_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id        INTEGER NOT NULL,
            subject_id      TEXT NOT NULL,
            schedule_day    TEXT NOT NULL,
            schedule_start  TEXT NOT NULL,
            schedule_end    TEXT NOT NULL,
            FOREIGN KEY (guild_id, subject_id) REFERENCES enrollment(guild_id, subject_id)
        );
    """,

    'homework': """
        CREATE TABLE IF NOT EXISTS homeworks (
            homework_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id        INTEGER NOT NULL,
            subject_id      TEXT NOT NULL,
            homework_desc   TEXT NOT NULL,
            homework_end    TEXT NOT NULL,
            FOREIGN KEY (guild_id, subject_id) REFERENCES enrollment(guild_id, subject_id)
        )
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
            ownership_id
        ) VALUES (?, ?, ?)
    """,

    'enrollment': """
        INSERT INTO enrollments (
            guild_id,
            subject_id
        ) VALUES (?, ?)
    """,

    'schedule': """
        INSERT INTO schedules (
            guild_id,
            subject_id,
            schedule_day,
            schedule_start,
            schedule_end
        ) VALUES (?, ?, ?, ?, ?)
    """,

    'homework': """
        INSERT INTO homeworks (
            guild_id,
            subject_id,
            homework_desc,
            homework_end
        ) VALUES (?, ?, ?, ?)

    """
}

delete = {
    'guild': """
        DELETE FROM guilds
        WHERE guild_id = ?
    """,

    'subject': """
        DELETE FROM subjects
        WHERE subject_id = ? AND ownership_id = ?
    """,

    'enrollment': """
        DELETE FROM enrollments
        WHERE guild_id = ? AND subject_id = ?
    """,

    'enrollment_with_ids': """
        DELETE FROM enrollments
        WHERE subject_id = ?
    """,

    'homework': """
        DELETE FROM homeworks
        WHERE homework_id = ?
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
        WHERE schedule_id = ? AND guild_id = ?
    """,

    'private->public': """
        UPDATE subjects
        SET subject_privacy = FALSE
        WHERE subject_id = ? AND ownership_id = ?
    """,

    'public->private': """
        UPDATE subjects
        SET subject_privacy = TRUE
        WHERE subject_id = ? AND ownership_id = ?
    """
}

read = {
    'utc': """
        SELECT guild_utc 
        FROM guilds 
        WHERE guild_id = ?
    """,

    'public_subjects': """
        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE subject_privacy = FALSE
        ORDER BY subject_id ASC 
    """,

    'available_subjects': """
        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE subject_privacy = FALSE

        UNION

        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE ownership_id = ?

        ORDER BY subject_id ASC
    """,

    'owned_subjects': """
        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE ownership_id = ?
        ORDER BY subject_id ASC
    """,

    'owned_private_subjects': """
        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE ownership_id = ? AND subject_privacy = TRUE
        ORDER BY subject_id ASC
    """,

    'search_subject': """
        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE subject_id = ? AND subject_privacy = FALSE

        UNION

        SELECT subject_id, subject_name 
        FROM subjects 
        WHERE subject_id = ? AND ownership_id = ?

        ORDER BY subject_id ASC
    """,

    'search_subject_id_all': """
        SELECT subject_id
        FROM subjects
        WHERE subject_id = ?
    """,

    'subject_from_code_in_guild': """
        SELECT subject_id, subject_name
        FROM subjects
        WHERE subject_id = ? AND ownership_id = ?
    """,

    'enrolled_subject_from_code': """
        SELECT enrollments.subject_id, subject_name
        FROM enrollments
        INNER JOIN subjects ON enrollments.subject_id = subjects.subject_id
        WHERE enrollments.subject_id = ? AND ownership_id = ?
    """,

    'enrolled_subjects': """
        SELECT enrollments.subject_id, subject_name
        FROM enrollments
        INNER JOIN subjects ON enrollments.subject_id = subjects.subject_id
        WHERE guild_id = ?
        ORDER BY enrollments.subject_id ASC
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
    """,

    'homeworks_from_guild': """
        SELECT homework_id, subject_name, homework_desc, homework_end
        FROM homeworks
        INNER JOIN subjects ON homeworks.subject_id = subjects.subject_id
        WHERE homeworks.guild_id = ?
        ORDER BY homework_end ASC
    """,

    'homework_from_id': """
        SELECT subject_name, homework_desc, homework_end
        FROM homeworks
        INNER JOIN subjects ON homeworks.subject_id = subjects.subject_id
        WHERE homeworks.guild_id = ? AND homework_id = ?
    """
}