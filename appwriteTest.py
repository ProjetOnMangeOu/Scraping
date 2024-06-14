from json import load
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

from dotenv import load_dotenv
import os 

load_dotenv()


client = Client()

(client
  .set_endpoint('https://cloud.appwrite.io/v1') # Your API Endpoint
  .set_project(os.getenv("projectId")) # Your project ID
  .set_key(os.getenv("apiKeyAppWrite")) # Your secret API key
  .set_self_signed() # Use only on dev mode with a self-signed SSL cert
)


databases = Databases(client)

databaseId = os.getenv("databaseId")



def seed_database():
  Restaurant = {
    'title': "Buy apples",
    'description': "At least 2KGs",
    'isComplete': True
  }

  databases.create_document(
    database_id=todoDatabase['$id'],
    collection_id=todoCollection['$id'],
    document_id=ID.unique(),
    data=testTodo1
  )

