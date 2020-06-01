from fastapi import FastAPI, Request, status, Depends, HTTPException
from pydantic import BaseModel
from transactionhist import *
import pickle
import time
from masterDB import *
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from dotenv import load_dotenv
import os
from os.path import join, dirname
from mainhelp import *
from userDB import *

pkl_file = open('cats_new.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

# to run the app vvv
# uvicorn main:app --reload


# Instansiate FastAPI Class
# when running the model, "main" is the python file and "app"
# is the variable name that is holding the FastAPI class (main:app)


# Load the file from the path
load_dotenv()

AUSERNAME = os.getenv("AUSERNAME", default="OOPS")
PASSWORD = os.getenv("PASSWORD", default="OOPS")

app = FastAPI()


templates = Jinja2Templates(directory="templates")


security = HTTPBasic()  


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, AUSERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Basic"},
    )
    return credentials.username

@app.get("/")
def root():
    # Written as a dict but returns a json object
    return {"message": 'Hello World!'}

# End point for the web backend to send transaction history objects and get back the same object w/ BB categories
@app.post("/transaction/")
def transaction(full_dict: dict):
    start_time = time.time()
    trans = TransactionHistory(full_dict=full_dict)
    user_id = full_dict['user_id']
    request = trans.getCats(cats_dict=getUser(user_id))
    print("--- %s seconds ---" % (time.time() - start_time))
    return request

@app.get("/admin/reset_master/")
def reset_master(username: str = Depends(get_current_username)):
    resetMaster()
    return{"message": "Master DB has been reset"}

# Admin route to edit the master DB table through an interface
@app.get("/admin/edit_master")
async def testing(request: Request,
                  Cat: str = 'None',
                  Plaid_cat: str = 'None',
                  Destination: str = 'None',
                  username: str = Depends(get_current_username)):

    # If Value and Destination have values, update the database
    if (Plaid_cat != 'None') & (Destination != 'None'):
        # Function that updates the master DB table
        updateMaster(old_cat = Cat, plaid_cat = Plaid_cat, destination = Destination)
        return {"message": f"The master table was successfully updated. {Plaid_cat} was moved from {Cat} to {Destination}."}

    # Pull the current default from the master DB table
    Dict = masterPull()
    
    # Use the helper function DictHTML to have 2 dictionaries:
        # one for displaying readable Plaid categories to the user and one for using to change the DB later
    html_dict, spaces_dict = DictHTML(Dict)
    
    # If a category is chosen, save a zipped version of the two different lists (readable and useful) of values to 'value_list'
    if Cat != 'None':
        value_list = zip(html_dict[Cat], spaces_dict[Cat])  
    else:
        value_list = 'None'
    
    # Save the Budget Block categories to the variable 'cats'
    cats = list(html_dict.keys())

    # Return the admin.html template with the appropriate variables in the context parameter
    return templates.TemplateResponse("admin.html",
                                     {'request': request,
                                      'cats': cats,
                                      'Cat': Cat,
                                      'Dict': Dict,
                                      'Plaid_cat': Plaid_cat,
                                      'Destination': Destination,
                                      'Value_list': value_list})

# Route that allows us to check the current values of the SQLite master table
@app.get("/admin/db")
async def db(request: Request,
             username: str = Depends(get_current_username)):
    master = masterPull()
    keys = list(master.keys())

    return templates.TemplateResponse("db.html",
                                     {'request': request,
                                      'keys': keys,
                                      'values': master})

# Route that allows us to reset/create the users table
@app.get("/admin/reset_user")
async def user(username: str = Depends(get_current_username)):
    resetUserTable()
    return {"message": "User DB has been reset"}

@app.post("/update_users")
async def update_users(expected: dict):
    new = changePreferences(expected)
    return({"message": new})
