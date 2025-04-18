import datetime
import json
from PIL import ImageGrab
import chromadb
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_community.document_loaders.pdf import OnlinePDFLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
import ollama
from bs4 import BeautifulSoup
import requests
from utils import download_pdf_from_url, print_webpage_as_pdf
import os

class toolsFactory:
    def __init__(self, db, doc_db):
        self.db = db
        self.doc_db = doc_db
        self.update_register()
        self.active_tools = {}
        for tool_name_i in self.register:
            self.active_tools[tool_name_i] = False
        self.update_tools()
    
    def update_register(self):
        self.register = {
            'get_current_date_and_time' : get_current_date_and_time(),
            'get_screenshot_description' : get_screenshot_description(),
            'search_google_news' : search_google_news(),
            # 'get_pokemon_screen_description' : get_pokemon_screen_description(),
            # 'search_google_scholar':search_google_scholar(),
            'search_academic_papers':search_academic_papers(),
            'search_long_term_memory' : search_long_term_memory(self.db),
            'search_document' : search_document(self.doc_db)
        }

        self.dont_add_to_long_term_memory = [
            'search_long_term_memory',
            'search_document',
            'search_google_news'
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
        # You are playing pokemon firered, you can move around using "left", "right", "up" or "down" commands or "a" to interact or accept and "b" to cancel or back. press "start" to open the menu. What is your next command?
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
        message = f'''This is a scene from Pokemon firered game, \
        the player is in its room at the beggining of the game, \
        What steps should the player take to get out of the room?'''
        response = ollama.chat(model='llava-llama3', messages=[{'role':'user', 'content':message, 'images':[filePath]}], options={'seed':42, "temperature":0})
        return response['message']['content']

class search_long_term_memory:
    def __init__(self, db):
        self.db = db
        self.type = 'function'
        self.name = 'search_long_term_memory'
        self.description = f"""\
        Search provided memory document and retrieve fragments relate to a topic or phrase as context.\
        Result may not be related to the topic searched, in this case, ignore the results.\
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
            search_result = "You remember from previous chat:"
            for i, result_i in enumerate(docs[:n_results]):
                search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
                i = i +1
        return search_result

class search_document:
    def __init__(self, doc_db):
        self.doc_db = doc_db
        self.type = 'function'
        self.name = 'search_document'
        self.description = f"""\
        search provided document file and retrieve fragments related to topic or phrase\
        """
        self.parameters = {
            'type': 'object',
            'properties': {
                'prompt_to_search':{
                    'type' : 'string',
                    'description': 'The topic or phrase to search in the document'
                }
            },
            'required': ['prompt_to_search'],
          }
    
    def function(self, prompt_to_search: str, n_results: int = 2):
        if self.doc_db is None:
            search_result = ""
        else:
            docs = self.doc_db.similarity_search(prompt_to_search)
            search_result = ""
            for i, result_i in enumerate(docs[:n_results]):
                search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
                i = i +1
        return search_result

class search_google_news:
    def __init__(self):
        self.type = 'function'
        self.name = 'search_google_news'
        self.description = f"""\
        return a string with the latest news headlines from google news\
        """
        self.parameters = {
            'type': 'object',
            'properties': {
                'topic_to_search':{
                    'type' : 'string',
                    'description': 'The topic or phrase to search in the news'
                }
            },
            'required': ['topic_to_search'],
          }
    
    def function(self, topic_to_search: str):
        default_header_template = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*"
                ";q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        loader = WebBaseLoader(f"https://news.google.com/search?q={topic_to_search}&hl=en-GB&gl=GB&ceid=GB%3Aen",
                               header_template=default_header_template,
                               requests_kwargs = {'cookies':{"_ga":"GA1.1.1553810516.1725728050",
                                                             "_ga_SYGF1G18MM" : "GS1.1.1725728050.1.0.1725728050.0.0.0",
                                                             "GN_PREF":"W251bGwsIkNBSVNEQWl3aXZLMkJoRHdxY0QtQWciXQ__",
                                                             "NID":"517=pse__xXD_xGb_QSqcvPgkqJaXUSXM4zL_-YAyl64rQgUtwN0jGYtnEJjIbeM2ffWxPaDY1fyRJ5Xxe-DfU_VYrZn81m8Q2hsGstMgJVgadQAezG7hzhm1L1eSiYjCxHcihz1VU6saMLxBJI0AAMOy3x9hiIEevX8Xdk8SxnY8HtKNxoknA_12g",
                                                             "OTZ":"7723734_52_56_123900_52_436380",
                                                             "SOCS":"CAISOAgLEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjQwOTAzLjA0X3AwGgVlbi1HQiACGgYIgK_utgY"}})
        raw_documents = loader.load()
        # text_splitter = SemanticChunker(OllamaEmbeddings(model="nomic-embed-text"),breakpoint_threshold_type="gradient")
        # documents = text_splitter.split_documents(raw_documents)
        # db = Chroma.from_documents(documents, OllamaEmbeddings(model="nomic-embed-text"))
        # docs = db.similarity_search(topic_to_search)
        # search_result = ""
        # for i, result_i in enumerate(docs):
        #     search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
        #     i = i +1
        return str(raw_documents[0])

class search_google_scholar:
    def __init__(self):
        self.type = 'function'
        self.name = 'search_google_scholar'
        self.description = f"""\
        return a list with a brief summary of academic papers from google scholar, each item in the list has a title, snippet, authors, and link\
        """
        self.parameters = {
            'type': 'object',
            'properties': {
                'topic_to_search':{
                    'type' : 'string',
                    'description': 'The topic or phrase to search in google scholar'
                }
            },
            'required': ['topic_to_search'],
          }
    
    def function(self, topic_to_search: str):
        requests_kwargs = {'cookies':{"_ga":"GA1.1.1553810516.1725728050",
                                      "_ga_SYGF1G18MM" : "GS1.1.1725728050.1.0.1725728050.0.0.0",
                                      "GN_PREF":"W251bGwsIkNBSVNEQWl3aXZLMkJoRHdxY0QtQWciXQ__",
                                      "NID":"517=pse__xXD_xGb_QSqcvPgkqJaXUSXM4zL_-YAyl64rQgUtwN0jGYtnEJjIbeM2ffWxPaDY1fyRJ5Xxe-DfU_VYrZn81m8Q2hsGstMgJVgadQAezG7hzhm1L1eSiYjCxHcihz1VU6saMLxBJI0AAMOy3x9hiIEevX8Xdk8SxnY8HtKNxoknA_12g",
                                      "OTZ":"7723734_52_56_123900_52_436380",
                                      "SOCS":"CAISOAgLEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjQwOTAzLjA0X3AwGgVlbi1HQiACGgYIgK_utgY"}}
        
        ## get google scholar results
        r = requests.get(f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={topic_to_search}", **requests_kwargs)
        soup = BeautifulSoup(r.text, 'html.parser')
        all_matches = soup.find_all("div", {'class':'gs_r gs_or gs_scl'})
        parsed_result = []
        for result_i in all_matches:
            try:
                link = result_i.find("div", {'class':'gs_or_ggsm'}).find('a')['href']
            except:
                link = result_i.find("div", {'class':'gs_ri'}).find('a')['href']
            parsed_result_temp  = {'title' : result_i.find('h3', {'class':'gs_rt'}).find('a').text,
                                   'snippet' : result_i.find('div', {'class':'gs_rs'}).text,
                                   'authors' : result_i.find('div', {'class':'gs_a'}).text,
                                   'link' : link
                                   }
            parsed_result.append(parsed_result_temp)
        return str(parsed_result)
    

class search_academic_papers:
    def __init__(self):
        self.type = 'function'
        self.name = 'search_academic_papers'
        self.description = f"""\
        return excerpts of academic papers related to the topic searched with the objective of answering a specific question.\
        """
        self.parameters = {
            'type': 'object',
            'properties': {
                'question_to_answer': {
                    'type' : 'string',
                    'description' : 'The question or problem that the search is trying to solve'
                },
                'topic_to_search':{
                    'type' : 'string',
                    'description': 'The topic or phrase to search in google scholar'
                }
            },
            'required': ['question_to_answer','topic_to_search'],
          }
    
    def function(self, question_to_answer: str, topic_to_search: str):
        search = search_google_scholar()
        search_results = search.function(topic_to_search)
        parsed_result = eval(search_results)

        ## create chromadb collection with results
        model = "nomic-embed-text"
        collection_name = topic_to_search.replace(" ", "_")
        try:
            client = chromadb.Client()
            collection = client.create_collection(name=collection_name)
            for i, result_i in  enumerate(parsed_result):
                embedding_i = ollama.embeddings(model=model, prompt=result_i['snippet'])
                collection.add(
                    ids=[str(i)],
                    embeddings=[embedding_i['embedding']],
                    documents=[result_i['snippet']]
                )
        except:
            collection = client.get_collection(name=collection_name)
        
        ## get top results
        embbed_question = ollama.embeddings(prompt=question_to_answer, model=model)
        top_results = collection.query(query_embeddings=[embbed_question["embedding"]], n_results=3)
        print(top_results)
        top_results_dict_list = []
        for result_i in parsed_result:
            if result_i['snippet'] in top_results['documents'][0]:
                top_results_dict_list.append(result_i)
        print(top_results_dict_list)
        
        ## create dbs for top links
        search_result = ""
        num_docs = 2
        for i, result_i in enumerate(top_results_dict_list):
            path = result_i['link']
            print(path)
            doc_type = os.path.splitext(path)
            if doc_type[1] == '.pdf' or "/pdf/" in path:
                download_pdf_from_url(path, "./temp", f"temp_{str(i)}.pdf")
                loader = PyPDFLoader(f"./temp/temp_{str(i)}.pdf")
            else:
                print_webpage_as_pdf(path, "./temp", f"temp_{str(i)}.pdf")
                loader = PyPDFLoader(f"./temp/temp_{str(i)}.pdf")
            raw_documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap = 0)
            documents = text_splitter.split_documents(raw_documents)
            db = Chroma.from_documents(documents, 
                                       OllamaEmbeddings(model=model),
                                       collection_name=f"coll_{str(i)}")
            docs = db.similarity_search(question_to_answer, k=num_docs)
            for j, doc_result_i in enumerate(docs):
                search_result = f"{search_result}\n{j+i*num_docs+1}. {doc_result_i.page_content} ({result_i['authors'], result_i['link']})"
            db.delete_collection()
        
        return search_result
    
