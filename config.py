from pymongo import MongoClient

# Configuración de MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["proyecto_ll"]

# Colecciones
users_collection = db["users"]
subjects_collection = db["subjects"]

