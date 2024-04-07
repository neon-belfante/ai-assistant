import ollama
import datetime
import re
from langchain_community.document_loaders import TextLoader, PyPDFLoader, OnlinePDFLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path

class textGenerator:
    def __init__(self):
        self  = self

    def callOllama(self, prompt: str, message_hist: list, model :str, temperature: int = 0, db = None):
        start_time = datetime.datetime.now()
        print(f"Starting text generator: {start_time}")
        if db is not None:
            prompt_augmented = self.augmentWithLongTermMemory(prompt, db)
            prompt = prompt_augmented
        message_hist.append({'role': 'user', 'content':prompt})
        response = ollama.chat(model=model, messages=message_hist, options={"seed": 42, "temperature": temperature})
        message_hist.append({'role': 'assistant', 'content': response['message']['content']})
        print(f"Ended text generator: {datetime.datetime.now()} - Elapsed time = {datetime.datetime.now() - start_time}")
        return response['message']['content']
    
    def summariseText(self, prompt: str):
        message = f'''
        Summarise in one phrase: "{prompt}" as if describing a photo.
        '''
        response = ollama.chat(model='llama2', messages=[{'role':'user', 'content': message}], options={"seed" : 42, "temperature": 0})
        return response['message']['content']

    def defineEmotion(self, prompt: str, emotion_list: list):
        print(f"Starting Emotion generator: {datetime.datetime.now()}")
        message = f'''
        Choose one word that is best related to the text: "{prompt}".
        Answer with just one word.
        You must chose only ONE word from the list: "{emotion_list}".
        '''
        response = ollama.chat(model='gemma:2b', messages=[{'role':'user', 'content': message}], options={"seed" : 42, "temperature": 4})
        response_list = str(response['message']['content'])
        response_list = re.sub('[^A-Za-z0-9]+', ' ', response_list)
        response_list = re.sub(' +', ' ', response_list).replace("\n\n", " ").strip('\n').strip("\n\n").strip("\n\n").lower().split(" ")
        print(response_list)
        emotion_candidates = [i for i in emotion_list if i in response_list]
        emotion_candidates
        if len(emotion_candidates) == 0:
            emotion_chosen = "thinking"
        else:
            emotion_chosen = emotion_candidates[0]
        print(f"Ended Emotion generator: {datetime.datetime.now()}")
        return emotion_chosen
    
    def callImageReader(self, prompt:str, filePath: str):
        print(f"Starting FileReader: {datetime.datetime.now()}")
        message = f'''What is in this image?'''
        print(message)
        response = ollama.chat(model='llava', messages=[{'role':'user', 'content':message, 'images':[filePath]}], options={'seed':42, "temperature":0})
        print(response)
        print(f"Ended FileReader: {datetime.datetime.now()}")
        return f'''{prompt} "{response['message']['content']}"'''
    
    def callMessageHistSummariser(self, messages_hist: list):
        print(f"Starting Memory Summariser: {datetime.datetime.now()}")
        final_prompt = f'''
        Summarise the previous message history in topics"
        '''
        messages_hist.append({'role': 'user', 'content': final_prompt})

        response = ollama.chat(model='llama2', messages=messages_hist, options={"seed" : 42, "temperature": 0})
        print(f"Ended Memory Summariser: {datetime.datetime.now()}")
        return f'''\n{datetime.datetime.now().strftime("%Y-%B-%d")}:\n"{response['message']['content']}"'''
    
    def loadLongTermMemory(self, filePath: str):
        print(f"Start loading long term memory: {datetime.datetime.now()}")
        raw_documents =  TextLoader(filePath).load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)
        db = Chroma.from_documents(documents, OllamaEmbeddings())
        print(f"Ended loading long term memory: {datetime.datetime.now()}")
        return db
    
    def augmentWithLongTermMemory(self, prompt: str, db, n_results = 2):
        print(f"Start using long term memory: {datetime.datetime.now()}")
        docs = db.similarity_search(prompt)
        search_result = ""
        for i, result_i in enumerate(docs[:n_results]):
            search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
            i = i +1
        final_prompt = f'''
        {prompt}
        Use if relevant, you remember that: "{search_result}"
        '''
        print(f"Ended using long term memory: {datetime.datetime.now()}")
        return final_prompt