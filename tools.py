import datetime
import json
from PIL import ImageGrab
import ollama

class toolsFactory:
    def __init__(self, db):
        self.db = db
        self.update_register()
        self.update_tools()
        self.active_tools = {}
        for tool_name_i in self.register:
            self.active_tools[tool_name_i] = False
    
    def update_register(self):
        self.register = {
            'get_current_date_and_time' : get_current_date_and_time(),
            'get_screenshot_description' : get_screenshot_description(),
            'get_pokemon_screen_description' : get_pokemon_screen_description(),
            'search_long_term_memory' : search_long_term_memory(self.db)
        }

        self.dont_add_to_long_term_memory = [
            'search_long_term_memory'
        ]

    def update_tools(self):
        self.tools = []
        for name_i, tool_i in self.register.items():
            if self.active_tools[name_i]:
                self.tools.append(
                    {
                        'type' : tool_i.type,
                        'function' : {
                            'name' : tool_i.name,
                            'description' : tool_i.description,
                            'parameters' : {
                                'type' : tool_i.parameters['type'],
                                'properties' : tool_i.parameters['properties'],
                                'required' : tool_i.parameters['required']  
                            }
                        }
                    }
                )

class get_current_date_and_time:
    def __init__(self):
        self.type = 'function'
        self.name = 'get_current_date_and_time'
        self.description = f"""\
        Display current date and time\
        """
        self.parameters = {
            'type': 'object',
            'properties': {},
            'required': [],
          }
    
    def function(self):
        result = datetime.datetime.now().strftime("%Y %B %d, %A, %H:%M %p")
        return result


class get_screenshot_description:
    def __init__(self):
        self.type = 'function'
        self.name = 'get_screenshot_description'
        self.description = f"""\
        Generates a text description of what is currently being displayed in the screen\
        """
        self.parameters = {
            'type': 'object',
            'properties': {},
            'required': [],
          }
    
    def function(self):
        screenshot = ImageGrab.grab()
        filePath = "temp/screenshot.png"
        screenshot.save(filePath)
        screenshot.close()
        message = f'''Describe this screenshot with sufficient detail as to help a blind impaired person'''
        response = ollama.chat(model='llava-llama3', messages=[{'role':'user', 'content':message, 'images':[filePath]}], options={'seed':42, "temperature":0})
        return response['message']['content']

class get_pokemon_screen_description:
    def __init__(self):
        self.type = 'function'
        self.name = 'get_pokemon_screen_description'
        self.description = f"""\
        Generates a text description of what is currently being displayed in the pokemon game\
        """
        self.parameters = {
            'type': 'object',
            'properties': {},
            'required': [],
          }
    
    def function(self):
        screenshot = ImageGrab.grab()
        filePath = "temp/screenshot.png"
        screenshot.save(filePath)
        screenshot.close()
        message = f'''This is a scene from Pokemon firered game, describe it as to guide a vision impaired player to take his next action'''
        response = ollama.chat(model='llava', messages=[{'role':'user', 'content':message, 'images':[filePath]}], options={'seed':42, "temperature":0})
        return response['message']['content']

class search_long_term_memory:
    def __init__(self, db):
        self.db = db
        self.type = 'function'
        self.name = 'search_long_term_memory'
        self.description = f"""\
        search long term memory to remember previous conversation around a topic or phrase\
        """
        self.parameters = {
            'type': 'object',
            'properties': {
                'prompt_to_search':{
                    'type' : 'string',
                    'description': 'The topic or phrase to search in the long term memory'
                }
            },
            'required': ['prompt_to_search'],
          }
    
    def function(self, prompt_to_search: str, n_results: int = 2):
        if self.db is None:
            search_result = ""
        else:
            docs = self.db.similarity_search(prompt_to_search)
            filePath = "temp/screenshot.png"
            search_result = ""
            for i, result_i in enumerate(docs[:n_results]):
                search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
                i = i +1
        return search_result

# You are playing pokemon firered, you can move around using "left", "right", "up" or "down" commands or "a" to interact or accept and "b" to cancel or back. press "start" to open the menu. What is your next command?

