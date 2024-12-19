from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Conexión a MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
