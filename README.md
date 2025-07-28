# microserviceFullStack

## Running All Microservices Locally

Each microservice can be started individually using Uvicorn. Make sure you are in the `microserviceFullStack` directory and have installed all dependencies for each service.

**General Command Format:**
```
python -m uvicorn <service_folder>.main:app --host 0.0.0.0 --port <PORT> --reload
```

### Run Commands for Each Service

- **Gateway**
  ```
  python -m uvicorn gateway:app --host 0.0.0.0 --port 8000 --reload
  ```
- **admin_reply_service**
  ```
  python -m uvicorn admin_reply_service.main:app --host 0.0.0.0 --port 8001 --reload
  ```
- **announcement_email_service**
  ```
  python -m uvicorn announcement_email_service.main:app --host 0.0.0.0 --port 8002 --reload
  ```
- **announcement_service**
  ```
  python -m uvicorn announcement_service.main:app --host 0.0.0.0 --port 8003 --reload
  ```
- **comparison_document_service**
  ```
  python -m uvicorn comparison_document_service.main:app --host 0.0.0.0 --port 8004 --reload
  ```
- **otp_service**
  ```
  python -m uvicorn otp_service.main:app --host 0.0.0.0 --port 8005 --reload
  ```
- **project_service**
  ```
  python -m uvicorn project_service.main:app --host 0.0.0.0 --port 8006 --reload
  ```
- **service_tool_service**
  ```
  python -m uvicorn service_tool_service.main:app --host 0.0.0.0 --port 8007 --reload
  ```
- **support_ticket_service**
  ```
  python -m uvicorn support_ticket_service.main:app --host 0.0.0.0 --port 8008 --reload
  ```
- **translation_document_service**
  ```
  python -m uvicorn translation_document_service.main:app --host 0.0.0.0 --port 8009 --reload
  ```
- **user_service**
  ```
  python -m uvicorn user_service.main:app --host 0.0.0.0 --port 8010 --reload
  ```

> **Note:**
> - Ensure all environment variables are set (see each service's `.env` file).
> - Install dependencies for each service (usually with `pip install -r requirements.txt`).
> - If you use Docker, see each service's `Dockerfile` for containerized commands.
