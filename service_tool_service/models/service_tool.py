from microserviceFullStack.dependencies.db import db

def get_service_tool_collection():
    return db["service_tools"]
