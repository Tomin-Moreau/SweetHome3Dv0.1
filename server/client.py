import cmd
import json
import socket
import sys

class Client:
    def __init__(self, host="127.0.0.1", port=10004):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, self.port))

    def send_request(self, request):
        print(f"Sending request: {request}")
        self.client_socket.send(json.dumps(request).encode('utf-8'))
        response = self.client_socket.recv(4096).decode('utf-8')
        return json.loads(response)
    
    def recv_image(self, image_weight):
        image_data = b""
        while len(image_data) < image_weight:
            image_data += self.client_socket.recv(4096)
            print(len(image_data), "/", image_weight, "bytes received\n")
        return image_data

    def close(self):
        self.client_socket.close()

class CLI(cmd.Cmd):
    prompt = ">>> "

    def __init__(self, client):
        super().__init__()
        self.client = client

    def do_authenticate(self, arg):
        "Authenticate: authenticate username password"
        args = arg.split()
        if len(args) != 2:
            print("Usage: authenticate username password")
            return
        username, password = args
        request = {
            "command": "AUTHENTICATE",
            "username": username,
            "password": password,
        }
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_disconnect(self, arg):
        "Disconnect the user"
        request = {"command": "DISCONNECT"}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_add_user(self, arg):
        "Add a new user: add_user username password is_admin"
        args = arg.split()
        if len(args) != 3:
            print("Usage: add_user username password is_admin")
            return
        username, password, is_admin = args
        is_admin = is_admin.lower() in ["true", "1", "yes"]
        request = {
            "command": "SET",
            "table": "users",
            "username": username,
            "password": password,
            "is_admin": is_admin,
        }
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_add_fourniture(self, arg):
        "Add a new fourniture: add_fourniture name room type color x_dimension y_dimension image_path price (image_path can be 'None')"
        args = arg.split()
        if len(args) != 8:
            print("Usage: add_fourniture name room type color x_dimension y_dimension image_path price")
            return
        name, room, type, color, x_dimension, y_dimension, image_path, price = args
        request = {
            "command": "SET",
            "table": "fournitures",
            "name": name,
            "room": room,
            "type": type,
            "color": color,
            "x_dimension": int(x_dimension),
            "y_dimension": int(y_dimension),
            "image_path": image_path,
            "price": int(price)
        }
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_get_fourniture(self, arg):
        "Get fourniture details: get_fourniture id"
        args = arg.split()
        if len(args) != 1:
            print("Usage: get_fourniture id")
            return
        id = args[0]
        request = {"command": "GET", "table": "fournitures", "id": id}
        response = self.client.send_request(request)
        print(response)

        if response.get("image_path"):
            image_weight = response.get("image_weight")
            if image_weight:
                image_data = self.client.recv_image(image_weight)
                with open("received_image.png", "wb") as f:
                    f.write(image_data)
                print("Image received and saved as 'received_image.png'")

    def do_delete_fourniture(self, arg):
        "Delete a fourniture: delete_fourniture id"
        args = arg.split()
        if len(args) != 1:
            print("Usage: delete_fourniture id")
            return
        id = args[0]
        request = {"command": "DELETE", "table": "fournitures", "id": id}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_search(self, arg):
        "Search for fournitures: search key1=value1 key2=value2 ..."
        args = arg.split()
        query = {}
        for arg in args:
            key, value = arg.split('=')
            query[key] = value
        request = {"command": "SEARCH", "query": query}
        response = self.client.send_request(request)
        print(response)

    def do_add_room(self, arg):
        "Add a new room: add_room name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: add_room name")
            return
        name = args[0]
        request = {"command": "SET", "table": "rooms", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_delete_room(self, arg):
        "Delete a room: delete_room name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: delete_room name")
            return
        name = args[0]
        request = {"command": "DELETE", "table": "rooms", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_add_type(self, arg):
        "Add a new type: add_type name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: add_type name")
            return
        name = args[0]
        request = {"command": "SET", "table": "types", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_delete_type(self, arg):
        "Delete a type: delete_type name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: delete_type name")
            return
        name = args[0]
        request = {"command": "DELETE", "table": "types", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_add_color(self, arg):
        "Add a new color: add_color name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: add_color name")
            return
        name = args[0]
        request = {"command": "SET", "table": "colors", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_delete_color(self, arg):
        "Delete a color: delete_color name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: delete_color name")
            return
        name = args[0]
        request = {"command": "DELETE", "table": "colors", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_send_image(self, arg):
        "Send an image to the server: send_image image_path"
        args = arg.split()
        if len(args) != 1:
            print("Usage: send_image image_path")
            return
        image_path = args[0]
        with open(image_path, "rb") as f:
            image_data = f.read()
        request = {
            "command": "RECIEVE_IMAGE",
            "image_path": image_path,
            "image_weight": len(image_data)
        }
        self.client.send_request(request)
        self.client.client_socket.sendall(image_data)
        print("Image sent successfully")

    def do_get_room(self, arg):
        "Get room details: get_room [id]"
        args = arg.split()
        if len(args) > 1:
            print("Usage: get_room [id]")
            return
        request = {"command": "GET", "table": "rooms"}
        if len(args) == 1:
            request["id"] = args[0]
        response = self.client.send_request(request)
        print(response)

    def do_get_type(self, arg):
        "Get type details: get_type [id]"
        args = arg.split()
        if len(args) > 1:
            print("Usage: get_type [id]")
            return
        request = {"command": "GET", "table": "types"}
        if len(args) == 1:
            request["id"] = args[0]
        response = self.client.send_request(request)
        print(response)

    def do_get_color(self, arg):
        "Get color details: get_color [id]"
        args = arg.split()
        if len(args) > 1:
            print("Usage: get_color [id]")
            return
        request = {"command": "GET", "table": "colors"}
        if len(args) == 1:
            request["id"] = args[0]
        response = self.client.send_request(request)
        print(response)
    
    def do_get_user(self, arg):
        "Get user details: get_user [username]"
        args = arg.split()
        if len(args) > 1:
            print("Usage: get_user [username]")
            return
        request = {"command": "GET", "table": "users"}
        if len(args) == 1:
            request["id"] = args[0]
        response = self.client.send_request(request)
        print(response)

if __name__ == "__main__":
    client = Client()
    CLI(client).cmdloop()