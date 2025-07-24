from microBackend.dependencies.db import db
def get_project_collection():
    
    return db["projects"]
