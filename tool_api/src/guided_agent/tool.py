from abc import ABC

class Tool(ABC):
    def run(self, tool_input):
        raise NotImplemented
    
    def name(self):
        raise NotImplemented
    
    def description(self):
        raise NotImplemented
    
    def get_input_json_schema(self):
        raise NotImplemented