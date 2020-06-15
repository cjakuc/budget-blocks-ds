from fastapi import FastAPI, Request, status, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from routers import posts, admin

# to run the app vvv
# uvicorn main:app --reload


# Instansiate FastAPI Class
# when running the model, "main" is the python file and "app"
# is the variable name that is holding the FastAPI class (main:app)

tags_metadata = [
    {
        "name": "transaction",
        "description": "Automatically categorizes PLAID transactions into BudgetBlocks categories using the user's preferences or if they do not exist, the default preferences",
    },
    {
        "name": "census",
        "description": "Returns the categorized census average expenditures of the closest city in the census data or the region if the closest city is farther than 50 miles away",
    },
    {
        "name": "update_users",
        "description": "Updates a user's categorical preferences in the users table",
    },
    {
        "name": "Admin",
        "description": "Admin interface routes; accessible upon login through api.budgetblocks.org/admin"
    }
]

app = FastAPI(openapi_tags=tags_metadata)

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