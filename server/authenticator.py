class Authenticator:
    def __init__(self, database_thread):
        self.database_thread = database_thread
        self.is_authenticated = False
        self.is_admin = False

    def authenticate(self, username, password):
        self.database_thread.request_queue.put(
            ("AUTHENTICATE", {"username": username, "password": password})
        )
        self.is_authenticated = self.database_thread.response_queue.get()
        self.database_thread.request_queue.put(("IS_ADMIN", {"username": username}))
        self.is_admin = self.database_thread.response_queue.get()