import pytest
import socket
import threading
import json
import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.server import Server

server_port = 10012

class RealClient:
    def __init__(self, host="127.0.0.1", port=server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send_request(self, request):
        self.client_socket.send(json.dumps(request).encode('utf-8'))
        response = self.client_socket.recv(4096).decode('utf-8')
        return json.loads(response)
    
    def recv_image(self, image_weight):
        image_data = b""
        while len(image_data) < image_weight:
            image_data += self.client_socket.recv(4096)
            print(len(image_data),"/",image_weight,"bytes received\n")
        return image_data

    def close(self):
        self.client_socket.close()

@pytest.fixture(scope="module")
def server():
    server = Server(port=server_port,new_database=True,db_name="database_test.db")
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)

    yield server
    server.database_thread.stop()

@pytest.fixture
def client():
    client = RealClient("127.0.0.1", server_port)
    yield client
    client.close()

def test_authenticate_user(server, client):
    
    response = client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    assert response["MESSAGE"] == "Authentication successful"

def test_authenticate_user_fail(server, client):
    response = client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response["MESSAGE"] == "Authentication failed"

def test_disconnect(server, client):
    response = client.send_request({
        "command": "DISCONNECT"
    })
    assert response["MESSAGE"] == "Disconnected"


def test_add_user(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    
    response = client.send_request({
        "command": "SET",
        "table": "users",
        "username": "newuser",
        "password": "newpassword",
        "is_admin": False
    })
    assert response["MESSAGE"] == "User added successfully"
    response = client.send_request({
        "command": "SET",
        "table": "users",
        "username": "newuser",
        "password": "newpassword",
        "is_admin": False
    })
    assert response["MESSAGE"] == "User already exists"
    

def test_delete_user(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    response = client.send_request({
        "command": "SET",
        "table": "users",
        "username": "newuser2",
        "password": "newpassword",
        "is_admin": False
    })
    response = client.send_request({
        "command": "DELETE",
        "table": "users",
        "username": "newuser2"
    })
    
    assert response["MESSAGE"] == "User deleted successfully"


def test_add_room(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    response = client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Chambre"
    })
    assert response["MESSAGE"] == "Room added successfully"

def test_add_type(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    response = client.send_request({
        "command": "SET",
        "table": "types",
        "name": "chaise"
    })
        
        
def test_add_color(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    response = client.send_request({
        "command": "SET",
        "table": "colors",
        "name": "rouge"
    })
        
        
        
def test_remove_room(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    
    client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Chambre"
    })
    response = client.send_request({
        "command": "DELETE",
        "table": "rooms",
        "name": "Chambre"
    })
    
    assert response["MESSAGE"] == "Room deleted successfully"
    
def test_remove_type(server, client):
    
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    
    client.send_request({
        "command": "SET",
        "table": "types",
        "name": "chaise"
    })
    response = client.send_request({
        "command": "DELETE",
        "table": "types",
        "name": "chaise"
    })
    
    assert response["MESSAGE"] == "Type deleted successfully"
    
def test_remove_color(server, client):
    
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    
    client.send_request({
        "command": "SET",
        "table": "colors",
        "name": "rouge"
    })
    response = client.send_request({
        "command": "DELETE",
        "table": "colors",
        "name": "rouge"
    })
    
    assert response["MESSAGE"] == "Color deleted successfully"
    
    
    
    
    

def test_set_fourniture(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    request = {
        "command": "SET",
        "table": "fournitures",
        "name": "Chair1",
        "room": "Living Room",
        "type": "Furniture",
        "color": "Red",
        "x_dimension": 100,
        "y_dimension": 200,
        "image_path": "path/to/image"
    }
    response = client.send_request(request)
    assert response["MESSAGE"] == "Room not found"
    response = client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Living Room"
    })
    response = client.send_request(request)
    assert response["MESSAGE"] == "Type not found"
    response = client.send_request({
        "command": "SET",
        "table": "types",
        "name": "Furniture"
    })
    response = client.send_request(request)
    assert response["MESSAGE"] == "Color not found"
    response = client.send_request({
        "command": "SET",
        "table": "colors",
        "name": "Red"
    })
    response = client.send_request(request)
    assert response["MESSAGE"] == "Fourniture set successfully"
        

def test_search_fourniture(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    client.send_request({
        "command": "SET",
        "table": "colors",
        "name": "Blue"
    })
    client.send_request({
        "command": "SET",
        "table": "types",
        "name": "chair"
    })
    client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Bedroom"
    })
    client.send_request({
        "command": "SET",
        "table": "fournitures",
        "name": "Chair2",
        "room": "Bedroom",
        "type": "chair",
        "color": "Blue",
        "x_dimension": 100,
        "y_dimension": 200,
        "image_path": "path/to/image"
    })
    client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Kitchen"
    })
    client.send_request({
        "command": "SET",
        "table": "fournitures",
        "name": "Chair3",
        "room": "Kitchen",
        "type": "chair",
        "color": "Blue",
        "x_dimension": 100,
        "y_dimension": 200,
        "image_path": "path/to/image"
    })
    
    
    response = client.send_request({
        "command": "SEARCH",
        "query": {"name": "Chair2",
                  "room": "Bedroom",
                  "type": "chair",
                  "color": "Blue",
        }
    })
    assert len(response) > 0
    
    response = client.send_request({
        "command": "SEARCH",
        "query": {
                  "room": "Kitchen",
        }
    })
    assert len(response) > 0
    response = client.send_request({
        "command": "SEARCH",
        "query": {        }
    })
    assert len(response) > 1


def test_get_fourniture(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    client.send_request({
        "command": "SET",
        "table": "colors",
        "name": "Blue"
    })
    client.send_request({
        "command": "SET",
        "table": "types",
        "name": "chair"
    })
    client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Bedroom"
    })
    client.send_request({
        "command": "SET",
        "table": "fournitures",
        "name": "Chair2",
        "room": "Bedroom",
        "type": "chair",
        "color": "Blue",
        "x_dimension": 100,
        "y_dimension": 200,
        "image_path": "None"
    })
       
    search_result = client.send_request({
        "command": "SEARCH",
        "query": {"name": "Chair2",
                    "room": "Bedroom",
                    "type": "chair",
                    "color": "Blue",
            }})
    
    
    response = client.send_request({
        "command": "GET",
        "table": "fournitures",
        "id": search_result[0]["id"]
    })
    assert response["name"] == "Chair2"
    
    r1 = client.send_request({
        "command": "SET",
        "table": "fournitures",
        "name": "Chair3",
        "room": "Bedroom",
        "type": "chair",
        "color": "Blue",
        "x_dimension": 100,
        "y_dimension": 200,
        "image_path": "images/test.jpg"
    })
    
    search_result = client.send_request({
        "command": "SEARCH",
        "query": {"name": "Chair3",
                  "room": "Bedroom",
                  "type": "chair",
                  "color": "Blue",
        }
    })
    
    
    response = client.send_request({
        "command": "GET",
        "table": "fournitures",
        "id" : search_result[0]["id"]
    })
    
    
    # Receive the image from the server and save it to a file
    image_data = client.recv_image(response["image_weight"])
    with open("test.jpg", "wb") as f:
        f.write(image_data)
    
    # Check if the images are the same
    with open("images/test.jpg", "rb") as f:
        image1 = f.read()
    with open("test.jpg", "rb") as f:
        image2 = f.read()
    assert image1 == image2
    
    if os.path.exists("test.jpg"):
        os.remove("test.jpg")
        
        

def test_delete_fourniture(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    client.send_request({
        "command": "SET",
        "table": "colors",
        "name": "Blue"
    })
    client.send_request({
        "command": "SET",
        "table": "types",
        "name": "chair"
    })
    client.send_request({
        "command": "SET",
        "table": "rooms",
        "name": "Bedroom"
    })
    client.send_request({
        "command": "SET",
        "table": "fournitures",
        "name": "Chair2",
        "room": "Bedroom",
        "type": "chair",
        "color": "Blue",
        "x_dimension": 100,
        "y_dimension": 200,
        "image_path": "path/to/image"
    })
    
    search_result = client.send_request({
        "command": "SEARCH",
        "query": {"name": "Chair2",
                  "room": "Bedroom",
                  "type": "chair",
                  "color": "Blue",
        }
    })
    
    
    response = client.send_request({
        "command": "DELETE",
        "table": "fournitures",
        "id": search_result[0]["id"]
    })
    
    
    
    assert response["MESSAGE"] == "Fourniture deleted successfully"
    


def test_send_image(server, client):
    client.send_request({
        "command": "AUTHENTICATE",
        "username": "admin",
        "password": "admin"
    })
    with open("images/test.jpg", "rb") as f:
        image_data = f.read()
    
    req = {
        "command": "RECIEVE_IMAGE",
        "image_path": "images/test2.jpg",
        "image_weight": len(image_data)
    }
    
    client.client_socket.send(json.dumps(req).encode('utf-8'))
    client.client_socket.send(image_data)
    
    response = client.client_socket.recv(4096).decode("utf-8")
    with open("images/test2.jpg", "rb") as f:
        image_data2 = f.read()
    assert image_data == image_data2
    
    if os.path.exists("images/test2.jpg"):
        os.remove("images/test2.jpg")
        

