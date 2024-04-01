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

print(final_prompt)


##############################
ltm = open("long_term_memory.txt", "a")
ltm.write(str(messages_hist))
ltm.close()
#############################

import joblib
import ollama
import datetime
path = '/home/neon/Dropbox/Trabalho/Python/AI Assistant/birthday_message_hist_test.gz'
messages_hist = joblib.load(path)

final_prompt = f'''
Summarise the previous message history in topics"
'''
messages_hist.append({'role': 'user', 'content': final_prompt})

response = ollama.chat(model='llama2', messages=messages_hist, options={"seed" : 42, "temperature": 0})

print(f'''\n{datetime.datetime.now().strftime("%Y-%B-%d")}:\n"{response['message']['content']}"''')

###################################
lst = list(range(1,100))
lst[30:]
######
test_str = "meu_teste.gz"
now_0 = datetime.datetime.now()

timeDelta = datetime.datetime.now() - now_0


