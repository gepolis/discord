import logging
import sqlite3



class Users:
    def __init__(self, db):
        self.db = db

    def create_table(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                warns INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                lvl INTEGER DEFAULT 0
            )""")

    def get_user(self, user_id):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            return cur.fetchone()

    def reset_money(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET bank=?", ('0'))

    def add_money(self, user_id, money):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            m = int(cur.execute("SELECT bank FROM users WHERE user_id=?", (user_id,)).fetchone()[0])+money
            cur.execute("UPDATE users SET bank=? WHERE user_id=?", (m, user_id))

    def add_user(self, user_id):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    def remove_user(self, user_id):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))

    def get_all_users(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users")
            return cur.fetchall()

    def exists_user(self, user_id):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            if cur.fetchone() is not None:
                return True
            else:
                return False


class Tickets:
    def __init__(self, db):
        self.db = db
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                user_id INTEGE,
                closed INTEGER DEFAULT 0,
                channel INTEGER
            )""")

    def create_ticket(self,user,channel):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO tickets (user_id,channel) VALUES (?,?)", (user,channel,))

    def close_ticket(self,channel):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("UPDATE tickets SET closed=1 WHERE channel=?", (channel,))

    def count_tickets(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM tickets")
            return cur.fetchone()[0]

    def delete(self,channel):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM tickets WHERE channel=?", (channel,))

    def all_open_tickets(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT user_id,channel FROM tickets WHERE closed=0")
            return cur.fetchall()

    def exists(self,channel):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT channel FROM tickets WHERE channel=?", (channel,))
            if cur.fetchone() is not None:
                return True
            else:
                return False

class AssistentLogs:
    def __init__(self, db):
        self.db = db
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS assistent_logs (
                user_id INTEGER,
                ticket_channel TEXT
            )""")

    def add_log(self, user_id, ticket_channel):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO assistent_logs (user_id,ticket_channel) VALUES (?,?)", (user_id,ticket_channel,))

    def check_conut(self,user,count_to_up:20):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM assistent_logs WHERE user_id=?", (user,))
            count = cur.fetchone()[0]
            return count >= count_to_up


class MafiaRooms:
    def __init__(self, db):
        self.db = db
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS mafia_rooms (
                room_id INTEGER PRIMARY KEY,
                room_name TEXT,
                category_id INTEGER,
                
            )""")
