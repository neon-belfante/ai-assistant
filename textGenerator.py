import ollama
import datetime
import chromadb
import re
from langchain_community.document_loaders import TextLoader, PyPDFLoader, OnlinePDFLoader, Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path
import os

class textGenerator:
    def __init__(self):
        pass

    def callOllama(self, 
                   prompt: str, 
                   message_hist: list, 
                   model :str, 
                   temperature: int = 0, 
                   db = None, 
                   doc_db = None, 
                   use_tools_flag: bool = False,
                   tools_factory = None):
        start_time = datetime.datetime.now()
        print(f"Starting text generator: {start_time}")
        message_hist_augmented = message_hist.copy()
        message_hist.append({'role': 'user', 'content':prompt})
        if db is not None:
            tools_factory.db = db
            tools_factory.update_register()
            # prompt_augmented = self.augmentWithLongTermMemory(prompt, db)
            # prompt = prompt_augmented
        if doc_db is not None:
            tools_factory.doc_db = doc_db
            tools_factory.update_register()
            # prompt_augmented = self.augmentWithLongTermMemory(prompt, doc_db, is_document=True)
            # prompt = prompt_augmented
        message_hist_augmented.append({'role': 'user', 'content':prompt})
        print(prompt)
        if use_tools_flag:
            used_tool, tool_response = self.callTool(message_hist=message_hist_augmented, 
                                                     model=model, 
                                                     temperature=temperature,
                                                     tools_factory=tools_factory)
            if used_tool:
                response = ollama.chat(model=model, messages=message_hist_augmented + tool_response, options={"seed": 42, "temperature": temperature})
                for tool_response_i in tool_response:
                    message_hist.append(tool_response_i)
                n_tools = len(tool_response)
            else:
                response = tool_response
                n_tools = 0
        else:
            n_tools = 0
            response = ollama.chat(model=model, messages=message_hist_augmented, options={"seed": 42, "temperature": temperature})
        message_hist.append({'role': 'assistant', 'content': response['message']['content']})
        print(f"Ended text generator: {datetime.datetime.now()} - Elapsed time = {datetime.datetime.now() - start_time}")
        return response['message']['content'], n_tools
    
    def callTool(self, message_hist:list, model:str, temperature: int = 0, tools_factory=None):
        response = ollama.chat(
            model=model,
            messages=message_hist,
            tools= tools_factory.tools,
            options={"seed" : 42,
                     "temperature" : temperature}
        )

        # Check if the model decided to use the provided function
        if not response['message'].get('tool_calls'):
            used_tool = False
            tools_response = response
            print("The model didn't use the function.")
        
        # Process function calls made by the model
        if response['message'].get('tool_calls'):
            used_tool=True
            tools_response = []
            for tool in response['message']['tool_calls']:
                print(f"Calling tool {tool['function']['name']}: {datetime.datetime.now()}")
                function_response = tools_factory.register[tool['function']['name']].function(**tool['function']['arguments'])
                print(function_response)
                # Add function response to the conversation
                tools_response.append(
                    {
                    'role': 'tool',
                    'name': tool['function']['name'],
                    'content': function_response,
                    }
                )
        return used_tool, tools_response
    
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
    
    def defineEmotionUsingEmbeddings(self, prompt: str, emotion_list: list):
        print(f"Starting Emotion generator: {datetime.datetime.now()}")
        model = "nomic-embed-text"
        try:
            client = chromadb.Client()
            collection = client.create_collection(name="emotions")
            for i, emotion_i in enumerate(emotion_list):
                response = ollama.embeddings(model=model, prompt=f"*{emotion_i}*")
                embedding = response["embedding"]
                collection.add(
                    ids=[str(i)],
                    embeddings=[embedding],
                    documents=[emotion_i]
                )
        except:
            collection = client.get_collection(name="emotions")
        try:
            prompt_embedding = ollama.embeddings(prompt=prompt, model=model)
            results = collection.query(query_embeddings=[prompt_embedding["embedding"]], n_results=1)
            emotion_chosen = results["documents"][0][0]
        except:
            emotion_chosen = "thinking"
        print(emotion_chosen)
        if emotion_chosen not in emotion_list:
            emotion_chosen = "thinking"
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
    
    def loadDoc(self, filePath: str):
        print(f"Start loading doc: {datetime.datetime.now()}")
        dict_doc_types = {
            '.doc' : Docx2txtLoader(filePath),
            '.docx' : Docx2txtLoader(filePath),
            '.pdf' : PyPDFLoader(filePath),
            '.txt' : TextLoader(filePath)
        }
        doc_type = os.path.splitext(filePath)
        if doc_type[1] not in dict_doc_types.keys():
            print(f'not valid doc type, must be one of {dict_doc_types.keys()}')
        else:
            raw_documents =  dict_doc_types[doc_type[1]].load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
            documents = text_splitter.split_documents(raw_documents)
            db = Chroma.from_documents(documents, OllamaEmbeddings(model="nomic-embed-text"))
        print(f"Ended loading doc: {datetime.datetime.now()}")
        return db
    
    def loadLongTermMemory(self, filePath: str):
        print(f"Start loading long term memory: {datetime.datetime.now()}")
        raw_documents =  TextLoader(filePath).load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)
        db = Chroma.from_documents(documents, OllamaEmbeddings(model="nomic-embed-text"))
        print(f"Ended loading long term memory: {datetime.datetime.now()}")
        return db
    
    def augmentWithLongTermMemory(self, prompt: str, db, is_document: bool = False, n_results = 2):
        print(f"Start using long term memory: {datetime.datetime.now()}")
        docs = db.similarity_search(prompt)
        search_result = ""
        for i, result_i in enumerate(docs[:n_results]):
            search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
            i = i +1
        if is_document:
            final_prompt = f'''
            {prompt} 
            --The document reads: "{search_result}"
            '''
        else:
            final_prompt = f'''
            {prompt}
            --Use if relevant, you remember that: "{search_result}"
            '''
        # print(final_prompt)
        print(f"Ended using long term memory: {datetime.datetime.now()}")
        return final_prompt