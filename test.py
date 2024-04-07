from langchain_community.document_loaders import TextLoader, PyPDFLoader, OnlinePDFLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import ollama

ollama_emb = OllamaEmbeddings(
    model="gemma:2b",
)

raw_documents =  TextLoader('/home/neon/Dropbox/Trabalho/Python/AI Assistant/birthday_rag_test.txt').load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
db = Chroma.from_documents(documents, OllamaEmbeddings())


raw_documents_pdf = PyPDFLoader('/home/neon/Dropbox/Trabalho/EY/CAF- Belfante.pdf').load_and_split()
text_splitter_pdf = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
documents_pdf = text_splitter_pdf.split_documents(raw_documents_pdf)
db = Chroma.from_documents(documents_pdf, OllamaEmbeddings())

prompt = "What is the employee first name?"
embedding_vector = OllamaEmbeddings().embed_query(prompt)
embedding_vector


docs = db.similarity_search_by_vector(embedding_vector)
search_result = ""
for i, result_i in enumerate(docs[:2]):
    search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
    i = i +1
final_prompt = f'''
{prompt}
You remember that: "{search_result}"
'''


prompt = "What is the employee first name?"
docs = db.similarity_search(prompt)
search_result = ""
for i, result_i in enumerate(docs[:2]):
    search_result = f"{search_result}\n{i+1}. {result_i.page_content}"
    i = i +1
final_prompt = f'''
{prompt}
Use if relevant, you remember that: "{search_result}"
'''


response = ollama.chat(model='llama2', messages=[{'role':'user', 'content': final_prompt}], options={"seed" : 42, "temperature": 0})
response['message']['content']


######################################lang chain chat history#########
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import FileChatMessageHistory
import json

llm = ChatOllama(model="ella", temperature=0, seed=42)
prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
store = {}
chain = prompt | llm
local_store = FileChatMessageHistory(".\message_hist2.json")

with open(".\message_hist.json", "w") as f:
    json.dump(store['abc123'].json(), f)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return local_store


with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

with_message_history.invoke(
    {'input' : "Hi Ella, can you remember the number 7 for me?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "which number I asked you to remember?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "tell me your plans for the next videos of your channel"},
    config={"configurable": {"session_id": "abc123"}},
)

response = with_message_history.invoke(
    {'input' : "which number I asked you to remember?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "What are good places to visit in London?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "which number I asked you to remember?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "Tell me a really long story"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "which number I asked you to remember?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "Tell me another really long story"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "which number I asked you to remember?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "which number I asked you to remember?"},
    config={"configurable": {"session_id": "abc123"}},
)

with_message_history.invoke(
    {'input' : "what places you want to see?"},
    config={"configurable": {"session_id": "abc123"}},
)

with open(".\message_hist2.json", "r") as f, open("message_hist3", "w") as to:
    to_insert = json.load(f)
    json.dump(to_insert, to)

import os
os.remove(".\message_hist.json")

local_store.__class__
response.content
local_store.__dict__


llm = ChatOllama(model="llama2", temperature=0, seed=42)
prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
store = {}
chain = prompt | llm
local_store = FileChatMessageHistory(".\message_hist2.json")

def get_session_in_memory_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = local_store
    return store[session_id]

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_in_memory_history,
    input_messages_key="input",
    history_messages_key="history",
)

with_message_history.invoke(
    {'input' : "Summarise the previous message history in topics"},
    config={"configurable": {"session_id": "abc123"}},
)

with open("message_hist3", "r") as f:
    to_insert = json.load(f)

with open("message_hist3", "w") as to:
    json.dump(to_insert[:-2], to)
