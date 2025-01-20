import threading
import queue
from .database import Database
import os
class DatabaseThread(threading.Thread):
    def __init__(self, db_name="database.db",new_database=False):
        super().__init__()
        if new_database:
            #Remove the database file
            try:
                os.remove(db_name)
            except FileNotFoundError:
                pass
        
        
        
        self.database = Database(db_name)
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.image_queue = queue.Queue()

    def run(self):
        while True:
            request = self.request_queue.get()
            if request is None:
                break
            command, data = request
            response = self.handle_request(command, data)
            self.response_queue.put(response)

    def handle_request(self, command, data):
        if command == "GET":
            return self.handle_get(data)

        elif command == "SET":
            return self.handle_set(data)
        elif command == "DELETE":
            return self.handle_delete(data)
        elif command == "AUTHENTICATE":
            return self.database.authenticate_user(data["username"], data["password"])
        elif command == "IS_ADMIN":
            return self.database.is_admin(data["username"])
        elif command == "SEARCH":
            return self.handle_search(data)
            
        else:
            return "Invalid command"
        
    def handle_search(self, data):
        filters = data.get("filters", "")
        filter_on = data.get("filter_on", "")
        if filters:
            
            results_list = self.database.search(filters, filter_on)
            results_dict = []
            for result in results_list:
                fourniture = {
                    "id": result[0],
                    "name": result[1],
                    "room": result[2],
                    "type": result[3],
                    "color": result[4],
                    "x_dimension": result[6],
                    "y_dimension": result[7],
                    "image_path": result[5],
                }
                results_dict.append(fourniture)
   
            return results_dict
        
    def handle_set(self, data):
        
        table = data.get("table")
        
        
        
        if table == "fournitures":
            room_id = self.database.get_room_by_name(data["room"])
            type_id = self.database.get_type_by_name(data["type"])
            color_id = self.database.get_color_by_name(data["color"])
            # name_already_exists = self.database.get_fourniture_by_name(data["name"])
            if room_id is None:
                return {"MESSAGE": "Room not found"}
            if type_id is None:
                return {"MESSAGE": "Type not found"}
            if color_id is None:
                return {"MESSAGE": "Color not found"}
            # if name_already_exists:
            #     return {"MESSAGE": "Fourniture name already exists"}
            else:
                self.database.set_fourniture(data["name"], room_id[0], type_id[0], color_id[0], data["x_dimension"], data["y_dimension"], data["image_path"],data["price"])
                return {"MESSAGE": "Fourniture set successfully","id": self.database.get_fourniture_by_name(data["name"])[0]}
            
        elif table == "rooms":
            room_already_exists = self.database.get_room_by_name(data["name"])
            if room_already_exists:
                return {"MESSAGE": "Room already exists"}
            else:
                self.database.add_room(data["name"])
                return {"MESSAGE": "Room added successfully", "id": self.database.get_room_by_name(data["name"])[0]}
        elif table == "types":
            type_already_exists = self.database.get_type_by_name(data["name"])
            if type_already_exists:
                return {"MESSAGE": "Type already exists"}
            else:
                self.database.add_type(data["name"])
                return {"MESSAGE": "Type added successfully", "id": self.database.get_type_by_name(data["name"])[0]}
        elif table == "colors":
            color_already_exists = self.database.get_color_by_name(data["name"])
            if color_already_exists:
                return {"MESSAGE": "Color already exists"}
            else:
                self.database.add_color(data["name"])
                return {"MESSAGE": "Color added successfully", "id": self.database.get_color_by_name(data["name"])[0]}
        elif table == "users":
            already_exists = self.database.get_user_by_name(data["username"])
            if already_exists:
                return {"MESSAGE": "User already exists"}
            else:
                self.database.add_user(data["username"], data["password"], data["is_admin"])
                return {"MESSAGE": "User added successfully"}
            
    def handle_delete(self, data):
        table = data.get("table")
        if table == "fournitures":
            return (
                "Fourniture deleted successfully"
                if self.database.delete_fourniture(data["id"])
                else "Fourniture not found"
            )
        elif table == "rooms":
            if self.database.get_room_by_name(data["name"]):
                self.database.remove_room(data["name"])
                return "Room deleted successfully"
            else:
                return "Room not found"
            
        elif table == "types":
            if self.database.get_type_by_name(data["name"]):
                self.database.remove_type(data["name"])
                return "Type deleted successfully"
            else:
                return "Type not found"
        elif table == "colors":
            if self.database.get_color_by_name(data["name"]):
                self.database.remove_color(data["name"])
                return "Color deleted successfully"
            else:
                return "Color not found"
        elif table == "users":
            if self.database.get_user_by_name(data["username"]):
                self.database.delete_user(data["username"])
                return "User deleted successfully"
            else:
                return "User not found"
        
        
    def handle_get(self, data):
        
        table = data.get("table")
        response = {}
        
        if table == "fournitures":
            fourniture = self.database.get_fourniture(data["id"])
            if fourniture[5] !="None":
                
                response = {
                    "id": fourniture[0],
                    "name": fourniture[1],
                    "room": fourniture[2],
                    "type": fourniture[3],
                    "color": fourniture[4],
                    "x_dimension": fourniture[6],
                    "y_dimension": fourniture[7],
                    "image_path": fourniture[5],
                }
                    
             
            else:
                response = {
                    "id": fourniture[0],
                    "name": fourniture[1],
                    "room": fourniture[2],
                    "type": fourniture[3],
                    "color": fourniture[4],
                    "x_dimension": fourniture[6],
                    "y_dimension": fourniture[7],
                    "image_path": None,
                }
                

        if table == "rooms":
            if data.get("name"):
                room = self.database.get_room_by_name(data["name"])
                if room:
                    response = {"name": room[1]}
            else:
                rooms = self.database.get_rooms()
                print(rooms)
                response = [{"id": room[0], "name": room[1]} for room in rooms]
                
        if table == "types":
            if data.get("name"):
                type = self.database.get_type_by_name(data["name"])
                if type:
                    response = {"name": type[1]}
            else:
                types = self.database.get_types()
                response = [{"id": type[0], "name": type[1]} for type in types]
                
        if table == "colors":
            if data.get("name"):
                color = self.database.get_color_by_name(data["name"])
                if color:
                    response = {"name": color[1]}
            else:
                colors = self.database.get_colors()
                response = [{"id": color[0], "name": color[1]} for color in colors]
                
        return response

    def stop(self):
        self.request_queue.put(None)
        self.join()