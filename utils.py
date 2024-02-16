import configparser
import os

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.sql_database import SQLDatabase, SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI

#from SQLDatabase import SQLDatabase

def read_properties_file(file_path):
    # check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found")
    
    # Initialize the configparser
    config = configparser.ConfigParser()
    
    # read the properties file
    config.read(file_path)
    
    # Access values
    db_path = config['DEFAULT_DB_PATH']['local_db_path']
    gemini_api_key = config['DEFAULT_DB_PATH']['gemini_api_key']
    
    return db_path, gemini_api_key


def get_properties(file_path):
    # PATH to the properties file
    file_path = 'config.properties'
    
    try: 
        db_path, gemini_api_key = read_properties_file(file_path)
        print("Database path", db)
        print("Gemini API Key", gemini_api_key)
        return db_path, gemini_api_key
    except FileNotFoundError as e:
        print(e)
        raise(e)
    
def get_llm(gemini_api_key):
    
    """
    Create an instance of Google Gemini Pro
    
    returns: 
    - llm: An instance of Google Gemini Pro
    """
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=gemini_api_key)
    
    return llm

def db_connection(db):
    db = SQLDatabase.from_uri(f'sqlit:///{db}')
    print(db.dialect)
    print(db.get_usable_table_names())
    resp = db.run("SELECT * FROM Employees LIMIT 10")
    print(resp)
    return db

def create_conversatonal_chain():   
    # Get properties
    db_path, gemini_api_key = get_properties('config.properties')
    
    # Create LLM
    llm = get_llm(gemini_api_key)
    
    # Connect to database
    db = db_connection(db_path)
    
    sql_prompt_template = """
    Only use the following tables:
    {table_info}
    Question: {input}
    
    Given an input question, first create a syntactically correct {dialect} query to run.
    
    Relevant pieces of previous conversation:
    {history}
    
    (You do not need to use these pieces of information if not relevant)
    Do not include ```,````sql and \n om the output. 
    """
    
    prompt = PromptTemplate(
        input_variables=["input","table_info", "dialect", "history"], 
        template=sql_prompt_template,
    )

    memory = ConversationBufferMemory(memory_key="history")
    try:
        memory.load()
        db_llm_chain = SQLDatabaseChain.from_llm(
            llm,db, prompt=prompt, memory=memory, return_direct=True, verbose=True
        )

        output_parser = StrOutputParser()
        chain = llm | output_parser

    except Exception as e:
        pass
        raise e
    return db_llm_chain, chain