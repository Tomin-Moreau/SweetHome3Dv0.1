import cmd
import json
import socket


class Client:
    def __init__(self, host="127.0.0.1", port=10003):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.possible_type = {}
        self.possible_color = {}
        self.possible_room = {}
        types = self.send_request({"command": "GET", "table": "type"})
        for t in types:
            self.possible_type[t["name"]] = t["id"]
        colors = self.send_request({"command": "GET", "table": "color"})
        for c in colors:
            self.possible_color[c["name"]] = c["id"]
        rooms = self.send_request({"command": "GET", "table": "room"})
        for r in rooms:
            self.possible_room[r["name"]] = r["id"]
            

    def send_request(self, request):
        self.socket.send(json.dumps(request).encode("utf-8"))
        response = self.socket.recv(4096).decode("utf-8")
        return json.loads(response)

    def close(self):
        self.socket.close()


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
            "command": "ADD_USER",
            "username": username,
            "password": password,
            "is_admin": is_admin,
        }
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_add_fourniture(self, arg):
        "Add a new fourniture: add_fourniture name room x_dimension y_dimension image_path"
        args = arg.split()
        if len(args) != 5:
            print("Usage: add_fourniture name room x_dimension y_dimension image_path")
            return
        name, room, x_dimension, y_dimension, path = args
        request = {
            "command": "SET",
            "table": "fourniture",
            "name": name,
            "room": room,
            "x_dimension": int(x_dimension),
            "y_dimension": int(y_dimension),
            "image_path": path,
        }
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_get_fourniture(self, arg):
        "Get fourniture details: get_fourniture name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: get_fourniture name")
            return
        name = args[0]
        request = {"command": "GET","table": "fourniture", "name": name}
        response = self.client.send_request(request)
        print(response)

    def do_add_color(self, arg):
        "Add a new color: add_color name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: add_color name")
            return
        name = args[0]
        request = {"command": "SET", "table": "color", "name": name}
        response = self.client.send_request(request)
        if response["MESSAGE"] == "Color added successfully":
            self.client.possible_color[name] = response["id"]
        print(response["MESSAGE"])
    
    def do_add_type(self, arg):
        "Add a new type: add_type name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: add_type name")
            return
        name = args[0]
        request = {"command": "SET", "table": "type", "name": name}
        response = self.client.send_request(request)
        if response["MESSAGE"] == "Type added successfully":
            self.client.possible_type[name] = response["id"]
        print(response["MESSAGE"])
    
    def do_add_room(self, arg):
        "Add a new room: add_room name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: add_room name")
            return
        name = args[0]
        request = {"command": "SET", "table": "room", "name": name}
        response = self.client.send_request(request)
        if response["MESSAGE"] == "Room added successfully":
            self.client.possible_room[name] = response["id"]
        print(response["MESSAGE"])
    
    
    def do_delete_fourniture(self, arg):
        "Delete a fourniture: delete_fourniture name"
        args = arg.split()
        if len(args) != 1:
            print("Usage: delete_fourniture name")
            return
        name = args[0]
        request = {"command": "DELETE", "name": name}
        response = self.client.send_request(request)
        print(response["MESSAGE"])

    def do_search(self, arg):
        "Search for fournitures: search query"
        args = arg.split()
        if len(args) != 1:
            print("Usage: search query")
            return
        query = args[0]
        request = {"command": "SEARCH", "query": query}
        response = self.client.send_request(request)
        print(response)

    def do_exit(self, arg):
        "Exit the CLI"
        self.client.close()
        return True
    
    
    def do_add(self,arg):
        "Add a new type, room or color: add type|room|color name"
        args = arg.split()
        if len(args) != 2:
            print("Usage: add type|room|color name")
            return
        table, name = args
        if table not in ["types", "rooms", "colors"]:
            print("Invalid table")
            return
        request = {"command": "SET", "table": table, "name": name}
        response = self.client.send_request(request)
        if response["MESSAGE"] == f"{table.capitalize()} added successfully":
            if table == "type":
                self.client.possible_type[name] = response["id"]
            if table == "room":
                self.client.possible_room[name] = response["id"]
            if table == "color":
                self.client.possible_color[name] = response["id"]
        print(response["MESSAGE"])
        
    def do_get(self, arg):
        "Get all types, rooms or colors: get type|room|color"
        args = arg.split()
        if len(args) != 1:
            print("Usage: get type|room|color")
            return
        table = args[0]
        if table not in ["types", "rooms", "colors"]:
            print("Invalid table")
            return
        request = {"command": "GET", "table": table}
        response = self.client.send_request(request)
        print(response)
    
    def do_filter(self, arg):
        "ADD or Remove a filter: filter key value or filter remove or filter get"
        args = arg.split()
        if len(args) == 2:
            key, value = args
            if key not in ["type", "room", "color"]:
                print("Invalid key")
                return
            if key == "type":
                if value not in self.client.possible_type:
                    print("Invalid value")
                    return
            if key == "room":
                if value not in self.client.possible_room:
                    print("Invalid value")
                    return
            if key == "color":
                if value not in self.client.possible_color:
                    print("Invalid value")
                    return
            request = {"command": "SET_FILTER", "filter_key": key, "filter_value": value}
            response = self.client.send_request(request)
                
            print(response["MESSAGE"])
        if len(args) == 1:
            if args[0] == "remove":
                request = {"command": "RESET_FILTERS"}
                response = self.client.send_request(request)
                print(response["MESSAGE"])
            if args[0] == "get":
                request = {"command": "GET_FILTER"}
                response = self.client.send_request(request)
                print(response)
        else:
            print("Usage: filter key value or filter remove")
            
    
    

if __name__ == "__main__":
    client = Client()
    CLI(client).cmdloop()
