from fastapi import FastAPI
from routers import support_ticket

app = FastAPI(title="Support Ticket Service")
app.include_router(support_ticket.router)

@app.get("/")
def root():
    return {"message": "Support Ticket Service running"}
