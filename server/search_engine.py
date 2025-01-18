class SearchEngine:
    def __init__(self, database_thread):
        self.database_thread = database_thread
        self.filter = {}
        self.filter_type = self.database_thread.database.get_filter()
        for key in self.filter_type:
            self.filter[key] = None

    def search(self, query):
        
        # Take query data and put into filter
        self.reset_filters()
        for key, value in query.items():
            if key in self.filter_type :
                self.set_filter(key, value)
                self.filter_type[key] = True
        
        self.database_thread.request_queue.put(("SEARCH",{"filters" : self.filter,"filter_on":self.filter_type}))
        return self.database_thread.response_queue.get()

    def set_filter(self, filter_key, filter_value):
        self.filter[filter_key] = filter_value

    def reset_filters(self):
        self.filter = {key: None for key in self.filter_type}
        self.filter_type = {key:False for key in self.filter_type}
        
    def get_filters(self):
        return self.filter