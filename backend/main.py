from fastapi import FastAPI
from routers import user

app = FastAPI()

app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "LegalAI backend is running"}
