from fastapi import FastAPI
# from routers import service_tool  # Uncomment and implement when router is ready

app = FastAPI(title="Service Tool Service")
# app.include_router(service_tool.router)

@app.get("/")
def root():
    return {"message": "Service Tool Service running"}
