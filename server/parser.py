import json

class Parser:
    def parse(self, request):
        try:
            return json.loads(request)
        except json.JSONDecodeError:
            return None