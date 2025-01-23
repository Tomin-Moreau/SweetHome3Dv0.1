import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="database.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (   
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL UNIQUE,
                                password TEXT NOT NULL,
                                is_admin BOOLEAN NOT NULL)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS types(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL UNIQUE)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS rooms(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS colors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE)"""
        )

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS fournitures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                room INTEGER NOT NULL,
                type INTEGER NOT NULL,
                color INTEGER NOT NULL,
                image_path TEXT,
                x_dimension INTEGER NOT NULL,
                y_dimension INTEGER NOT NULL,
                price INTEGER,
                FOREIGN KEY(room) REFERENCES room(id)
                    ON UPDATE RESTRICT
                    ON DELETE RESTRICT,
                FOREIGN KEY(type) REFERENCES type(id)
                    ON UPDATE RESTRICT
                    ON DELETE RESTRICT,
                FOREIGN KEY(color) REFERENCES color(id)
                    ON UPDATE RESTRICT
                    ON DELETE RESTRICT)
                """
        )

        self.conn.commit()

        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.add_user("admin", "admin", True)

    def get_fourniture(self, id):
        self.cursor.execute("SELECT * FROM fournitures WHERE id=?", (id,))
        return self.cursor.fetchone()
    
    def get_fourniture_by_name(self, name):
        self.cursor.execute("SELECT * FROM fournitures WHERE name=?", (name,))
        return self.cursor.fetchone()

    def set_fourniture(self, name, room,type,color, x_dimension, y_dimension, path,price):
        self.cursor.execute(
            "INSERT INTO fournitures (name, room, type, color, x_dimension, y_dimension, image_path,price) VALUES (?, ?, ?,?, ?, ?, ?, ?)",
            (name, room, type, color, x_dimension, y_dimension, path,price),
        )
        self.conn.commit()
        

    def delete_fourniture(self, id):
        self.cursor.execute("DELETE FROM fournitures WHERE id=?", (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    

    def add_user(self, username, password, is_admin):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (username, hashed_password, is_admin),
        )
        self.conn.commit()

    def delete_user(self, username):
        self.cursor.execute("DELETE FROM users WHERE username=?", (username,))
        self.conn.commit()
    
    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_password),
        )
        return self.cursor.fetchone() is not None
    
    def add_type(self, name):
        self.cursor.execute("INSERT INTO types (name) VALUES (?)", (name,))
        self.conn.commit()
    
    def add_room(self, name):
        self.cursor.execute("INSERT INTO rooms (name) VALUES (?)", (name,))
        self.conn.commit()
        
    def add_color(self, name):
        self.cursor.execute("INSERT INTO colors (name) VALUES (?)", (name,))
        self.conn.commit()
        
    def remove_type(self, name):
        self.cursor.execute("DELETE FROM types WHERE name=?", (name,))
        self.conn.commit()
        
    def remove_room(self, name):
        self.cursor.execute("DELETE FROM rooms WHERE name=?", (name,))
        self.conn.commit()
        
    def remove_color(self, name):
        self.cursor.execute("DELETE FROM colors WHERE name=?", (name,))
        self.conn.commit()
        
    def get_types(self):
        self.cursor.execute("SELECT * FROM types")
        return self.cursor.fetchall()
    
    def get_rooms(self):
        self.cursor.execute("SELECT * FROM rooms")
        return self.cursor.fetchall()
    
    def get_colors(self):
        self.cursor.execute("SELECT * FROM colors")
        return self.cursor.fetchall()
    
    def get_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    
    def get_user_by_name(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()
    
    def get_type_by_name(self, name):
        self.cursor.execute("SELECT * FROM types WHERE name=?", (name,))
        return self.cursor.fetchone()
    
    def get_room_by_name(self, name):
        self.cursor.execute("SELECT * FROM rooms WHERE name=?", (name,))
        return self.cursor.fetchone()
    
    def get_color_by_name(self, name):
        self.cursor.execute("SELECT * FROM colors WHERE name=?", (name,))
        return self.cursor.fetchone()
    
    def get_type_by_id(self, id):
        self.cursor.execute("SELECT * FROM types WHERE id=?", (id,))
        return self.cursor.fetchone()
    
    def get_room_by_id(self, id):
        self.cursor.execute("SELECT * FROM rooms WHERE id=?", (id,))
        return self.cursor.fetchone()
    
    def get_color_by_id(self, id):
        self.cursor.execute("SELECT * FROM colors WHERE id=?", (id,))
        return self.cursor.fetchone()
    
    def get_user_by_name(self, name):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (name,))
        return self.cursor.fetchone()
    
    
    
    
    
    

    def is_admin(self, username):
        self.cursor.execute("SELECT is_admin FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()
        return True if result[0] else False

    def search(self, filter_value, filter_type):
        request = "SELECT * FROM fournitures"
        join_clauses = []
        where_clauses = []
        values = []
        # remove name from filter_value and filter_type


        for key in filter_value:
            if filter_type[key] and key != "name":
                join_clauses.append(f"JOIN {key}s ON fournitures.{key} = {key}s.id")
                where_clauses.append(f"{key}s.name = ?")
                values.append(filter_value[key])

        if where_clauses:
            request += " " + " ".join(join_clauses)
            request += " WHERE " + " AND ".join(where_clauses)
            if filter_value.get("name"):
                request += " AND fournitures.name LIKE ?"
                values.append(filter_value["name"])
        
        elif filter_value.get("name"):
            request += " WHERE fournitures.name LIKE ?"
            values.append(filter_value["name"])

        

        self.cursor.execute(request, values)
        return self.cursor.fetchall()
                
        
        
        

    def close(self):
        self.conn.close()

    def get_filter(self):
        return {"type": True, "room": True, "color": True,"name": True}