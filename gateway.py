# FastAPI API Gateway for microBackend
# This gateway proxies requests to the appropriate microservice based on the route prefix

from fastapi import FastAPI, Request, Response
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="microBackend API Gateway")

# Service route mapping (prefix: service_url)
SERVICE_MAP = {
    "/user": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "/project": os.getenv("PROJECT_SERVICE_URL", "http://localhost:8002"),
    "/support_ticket": os.getenv("SUPPORT_TICKET_SERVICE_URL", "http://localhost:8003"),
    "/admin_reply": os.getenv("ADMIN_REPLY_SERVICE_URL", "http://localhost:8004"),
    "/otp": os.getenv("OTP_SERVICE_URL", "http://localhost:8005"),
    "/announcement": os.getenv("ANNOUNCEMENT_SERVICE_URL", "http://localhost:8006"),
    "/announcement_email": os.getenv("ANNOUNCEMENT_EMAIL_SERVICE_URL", "http://localhost:8007"),
    "/comparison-document": os.getenv("COMPARISON_DOCUMENT_SERVICE_URL", "http://localhost:8008"),
    "/translation-document": os.getenv("TRANSLATION_DOCUMENT_SERVICE_URL", "http://localhost:8009"),
    "/service_tool": os.getenv("SERVICE_TOOL_SERVICE_URL", "http://localhost:8010"),
}

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    # Determine which service to proxy to based on the first path segment
    for prefix, service_url in SERVICE_MAP.items():
        if full_path.startswith(prefix.strip("/")):
            target_url = f"{service_url}/{full_path}"
            break
    else:
        return Response("Not found", status_code=404)

    # Prepare the proxied request
    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method,
            target_url,
            headers=headers,
            content=body,
            params=request.query_params,
            timeout=60.0
        )
    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway:app", host="0.0.0.0", port=int(os.getenv("API_GATEWAY_PORT", 8000)), reload=True)