from fastapi import FastAPI, Request, status, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from routers import posts, admin

# to run the app vvv
# uvicorn main:app --reload


# Instansiate FastAPI Class
# when running the model, "main" is the python file and "app"
# is the variable name that is holding the FastAPI class (main:app)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    # allow_origin_regex="http://localhost:3000.*"
)

app.include_router(posts.router)
app.include_router(admin.router)

@app.get("/")
def root():
    # Written as a dict but returns a json object
    return {"message": 'Hello World!'}