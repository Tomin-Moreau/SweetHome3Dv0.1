import socket
import threading
import json
import os
from server.parser import Parser
from server.database_thread import DatabaseThread
from server.authenticator import Authenticator
from server.search_engine import SearchEngine

class Server:
    def __init__(self, host="127.0.0.1", port=10004,new_database=False,db_name="database.db"):
        self.host = host
        self.port = port
        self.parser = Parser()
        self.database_thread = DatabaseThread(new_database=new_database,db_name=db_name)
        self.database_thread.start()
        
        self.image_to_send = (False, None)

    def receive_image(self, client_socket, image_path, image_weight):
        image_data = b""
        while len(image_data) < image_weight:
            image_data += client_socket.recv(4096)
        with open(image_path, "wb") as f:
            f.write(image_data)
        return {"MESSAGE": "Image received"}
    def handle_client(self, client_socket):
        identity = Authenticator(self.database_thread)
        search_engine = SearchEngine(self.database_thread)
        try:
            while True:
                request = client_socket.recv(1024).decode("utf-8")
                if not request:
                    break

                data = self.parser.parse(request)
                print(f"Received request: {data}")
                if not data:
                    response = {"MESSAGE": "Invalid request"}
                else:
                    command = data.get("command")

                    # Authentication
                    if command == "AUTHENTICATE":
                        username = data.get("username")
                        password = data.get("password")
                        print("Here")
                        identity.authenticate(username, password)
                        response = (
                            {"MESSAGE": "Authentication successful"}
                            if identity.is_authenticated
                            else {"MESSAGE": "Authentication failed"}
                        )

                    elif command == "DISCONNECT":
                        identity.is_authenticated = False
                        identity.is_admin = False
                        response = {"MESSAGE": "Disconnected"}

                    # Commands without authentication and admin
                    elif command == "GET":
                        self.database_thread.request_queue.put(("GET", data))
                        response = self.database_thread.response_queue.get()
                        if (data["table"] == "fournitures"):
                            if response.get("image_path") is not None:
                                        image_path = response["image_path"]
                                        #ensure image exists
                                        if os.path.exists(os.path.abspath(image_path)):
                                            self.image_to_send = (True, image_path)
                                            response["image_weight"] = os.path.getsize(image_path)
                                        else:
                                            response["image_path"] = None
                                            response["image_weight"] = None
                                            response["MESSAGE"] = "Image not found"

                    elif command == "SEARCH":
                        response = search_engine.search(data.get("query", ""))

                    # elif command == "SET_FILTER":
                    #     filter_key = data.get("filter_key")
                    #     filter_value = data.get("filter_value")
                    #     search_engine.set_filter(filter_key, filter_value)
                    #     response = {"MESSAGE": f"Filter set: {filter_key} = {filter_value}"}

                    # elif command == "RESET_FILTERS":
                    #     search_engine.reset_filters()
                    #     response = {"MESSAGE": "All filters reset"}
                    
                    # elif command == "GET_FILTER":
                        
                    #     response = {"MESSAGE": search_engine.get_filters()}

                    else:
                        # Commands with authentication and admin
                        if identity.is_authenticated and identity.is_admin:
                            if command == "SET":
                                self.database_thread.request_queue.put(("SET", data))
                                response  = self.database_thread.response_queue.get()
                                
                                    
                            elif command == "DELETE":
                                self.database_thread.request_queue.put(("DELETE", data))
                                response = {
                                    "MESSAGE": self.database_thread.response_queue.get()
                                }
                            elif command == "RECIEVE_IMAGE":
                                image_path = data.get("image_path")
                                image_weight = data.get("image_weight")
                                
                                response = self.receive_image(
                                    client_socket, image_path, image_weight
                                )
                                
                                
                            else:
                                response = {"MESSAGE": "Invalid command"}
                        else:
                            response = {
                                "MESSAGE": "Authentication required or admin rights required or wrong command"
                            }

                response = json.dumps(response)
                client_socket.send(response.encode("utf-8"))
                if self.image_to_send[0]:
                    try : 
                        image_path = os.path.abspath(self.image_to_send[1])

                        with open(image_path, "rb") as f:
                            image = f.read()
                            client_socket.send(image)
                    except FileNotFoundError:
                        response = {"MESSAGE": "Image not found"}
                        response = json.dumps(response)
                        client_socket.send(response.encode("utf-8"))
                    self.image_to_send = (False, None)
                    
                    
        finally:
            client_socket.close()

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"[*] Listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, addr = server.accept()
                print(f"[*] Accepted connection from {addr}")
                client_handler = threading.Thread(
                    target=self.handle_client, args=(client_socket,)
                )
                client_handler.start()
        finally:
            self.database_thread.stop()
            server.close()


if __name__ == "__main__":
    server = Server()
    server.start()