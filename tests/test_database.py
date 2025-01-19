import pytest
import sqlite3
import os

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import Database

@pytest.fixture
def db():
    db = Database(":memory:")  # Use in-memory database for testing
    yield db
    db.close()

def test_users_table_exists(db):
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert db.cursor.fetchone() is not None

def test_type_table_exists(db):
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='types'")
    assert db.cursor.fetchone() is not None

def test_room_table_exists(db):
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rooms'")
    assert db.cursor.fetchone() is not None

def test_color_table_exists(db):
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='colors'")
    assert db.cursor.fetchone() is not None

def test_fournitures_table_exists(db):
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fournitures'")
    assert db.cursor.fetchone() is not None

def test_admin_user_exists(db):
    db.cursor.execute("SELECT * FROM users WHERE username='admin'")
    user = db.cursor.fetchone()
    assert user is not None
    assert user[1] == "admin"
    assert user[3] == 1  # is_admin should be True

def test_users_table_columns(db):
    db.cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in db.cursor.fetchall()]
    assert columns == ["id", "username", "password", "is_admin"]

def test_type_table_columns(db):
    db.cursor.execute("PRAGMA table_info(types)")
    columns = [info[1] for info in db.cursor.fetchall()]
    assert columns == ["id", "name"]

def test_room_table_columns(db):
    db.cursor.execute("PRAGMA table_info(rooms)")
    columns = [info[1] for info in db.cursor.fetchall()]
    assert columns == ["id", "name"]

def test_color_table_columns(db):
    db.cursor.execute("PRAGMA table_info(colors)")
    columns = [info[1] for info in db.cursor.fetchall()]
    assert columns == ["id", "name"]

def test_fournitures_table_columns(db):
    db.cursor.execute("PRAGMA table_info(fournitures)")
    columns = [info[1] for info in db.cursor.fetchall()]
    assert columns == ["id", "name", "room", "type", "color", "image_path", "x_dimension", "y_dimension","price"]

def test_add_user(db):
    db.add_user("testuser", "password", False)
    db.cursor.execute("SELECT * FROM users WHERE username='testuser'")
    user = db.cursor.fetchone()
    assert user is not None
    assert user[1] == "testuser"
    assert user[3] == 0  # is_admin should be False

def test_authenticate_user(db):
    db.add_user("testuser", "password", False)
    assert db.authenticate_user("testuser", "password") is True
    assert db.authenticate_user("testuser", "wrongpassword") is False

def test_add_type(db):
    db.add_type("Chair")
    db.cursor.execute("SELECT * FROM types WHERE name='Chair'")
    type_ = db.cursor.fetchone()
    assert type_ is not None
    assert type_[1] == "Chair"

def test_add_room(db):
    db.add_room("Living Room")
    db.cursor.execute("SELECT * FROM rooms WHERE name='Living Room'")
    room = db.cursor.fetchone()
    assert room is not None
    assert room[1] == "Living Room"

def test_add_color(db):
    db.add_color("Red")
    db.cursor.execute("SELECT * FROM colors WHERE name='Red'")
    color = db.cursor.fetchone()
    assert color is not None
    assert color[1] == "Red"

def test_remove_type(db):
    db.add_type("Chair")
    db.remove_type("Chair")
    db.cursor.execute("SELECT * FROM types WHERE name='Chair'")
    type_ = db.cursor.fetchone()
    assert type_ is None

def test_remove_room(db):
    db.add_room("Living Room")
    db.remove_room("Living Room")
    db.cursor.execute("SELECT * FROM rooms WHERE name='Living Room'")
    room = db.cursor.fetchone()
    assert room is None

def test_remove_color(db):
    db.add_color("Red")
    db.remove_color("Red")
    db.cursor.execute("SELECT * FROM colors WHERE name='Red'")
    color = db.cursor.fetchone()
    assert color is None

def test_get_types(db):
    db.add_type("Chair")
    types = db.get_types()
    assert len(types) == 1
    assert types[0][1] == "Chair"

def test_get_rooms(db):
    db.add_room("Living Room")
    rooms = db.get_rooms()
    assert len(rooms) == 1
    assert rooms[0][1] == "Living Room"

def test_get_colors(db):
    db.add_color("Red")
    colors = db.get_colors()
    assert len(colors) == 1
    assert colors[0][1] == "Red"

def test_get_type_by_name(db):
    db.add_type("Chair")
    type_ = db.get_type_by_name("Chair")
    assert type_ is not None
    assert type_[1] == "Chair"

def test_get_room_by_name(db):
    db.add_room("Living Room")
    room = db.get_room_by_name("Living Room")
    assert room is not None
    assert room[1] == "Living Room"

def test_get_color_by_name(db):
    db.add_color("Red")
    color = db.get_color_by_name("Red")
    assert color is not None
    assert color[1] == "Red"

def test_set_fourniture(db):
    db.add_room("Living Room")
    db.add_type("Chair")
    db.add_color("Red")
    db.set_fourniture("Chair1", 1, 1, 1, 100, 200, "path/to/image",100)
    db.cursor.execute("SELECT * FROM fournitures WHERE name='Chair1'")
    fourniture = db.cursor.fetchone()
    assert fourniture is not None
    assert fourniture[1] == "Chair1"

def test_get_fourniture(db):
    db.add_room("Living Room")
    db.add_type("Chair")
    db.add_color("Red")
    db.set_fourniture("Chair1", 1, 1, 1, 100, 200, "path/to/image",100)
    fourniture = db.get_fourniture(1)
    assert fourniture is not None
    assert fourniture[1] == "Chair1"

def test_get_fourniture_by_name(db):
    db.add_room("Living Room")
    db.add_type("Chair")
    db.add_color("Red")
    db.set_fourniture("Chair1", 1, 1, 1, 100, 200, "path/to/image",100)
    fourniture = db.get_fourniture_by_name("Chair1")
    assert fourniture is not None
    assert fourniture[1] == "Chair1"

def test_delete_fourniture(db):
    db.add_room("Living Room")
    db.add_type("Chair")
    db.add_color("Red")
    db.set_fourniture("Chair1", 1, 1, 1, 100, 200, "path/to/image",100)
    db.delete_fourniture(1)
    db.cursor.execute("SELECT * FROM fournitures WHERE name='Chair1'")
    fourniture = db.cursor.fetchone()
    assert fourniture is None

def test_is_admin(db):
    db.add_user("adminuser", "password", True)
    result = db.is_admin("adminuser")
    randomvar = True
    assert result is True
    db.add_user("normaluser", "password", False)
    assert db.is_admin("normaluser") is False

def test_search(db):
    db.add_room("Living Room")
    db.add_type("Chair")
    db.add_color("Red")
    db.set_fourniture("Chair1", 1, 1, 1, 100, 200, "path/to/image",100)
    filter_value = {"type": "Chair", "room": "Living Room", "color": "Red","name":"Chair1"}
    filter_type = {"type": True, "room": True, "color": True,"name":True}
    results = db.search(filter_value, filter_type)
    assert len(results) == 1
    assert results[0][1] == "Chair1"