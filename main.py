from fastapi import FastAPI, Request, status, Depends, HTTPException
from pydantic import BaseModel
from transactionhist import *
import pickle
import time
from DB.masterDB import *
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from dotenv import load_dotenv
import os
from os.path import join, dirname
from mainhelp import *
from DB.userDB import *
from fastapi.middleware.cors import CORSMiddleware
from census import census_totals

pkl_file = open('Pickle/cats_new.pkl', 'rb')
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

# Attempt to fix local testing issues with CORSMiddleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    # allow_origin_regex="http://localhost:3000.*"
)

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
    # Instantiate TransactionHistory object
    trans = TransactionHistory(full_dict=full_dict)

    # Get the user ID
    user_id = full_dict['user_id']

    # Get user preferences
    user_dict = getUser(user_id)

    # Recategorize the transactions
    transactions = trans.getCats(cats_dict=getUser(user_id))
    # request = trans.getCats(cats_dict=user_dict)

    # Retreive the census info for the right location and append it to the transactions JSON. Return it
    request = census_totals(transactions=transactions, location=full_dict['location'], user_dict=user_dict)

    print("--- %s seconds ---" % (time.time() - start_time))

    return request

@app.get("/admin")
def admin_main(request: Request,
               username: str = Depends(get_current_username)):
    return templates.TemplateResponse("admin_main.html",
                                     {'request': request})

@app.get("/admin/reset_master_confirmation")
def reset_master_confirmation(request: Request):
    return templates.TemplateResponse("master_confirmation.html",
                                     {'request': request})

@app.get("/admin/reset_user_confirmation")
def reset_user_confirmation(request: Request):
    return templates.TemplateResponse("user_confirmation.html",
                                     {'request': request})

@app.get("/admin/reset_master/")
def reset_master(request: Request, username: str = Depends(get_current_username)):
    resetMaster()
    message = "The master table was reset"
    return templates.TemplateResponse("reset_success.html",
                                     {'request': request,
                                      'message': message})

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

        # Update change log table
        updateChangeLog(plaid_cat = Plaid_cat, old_BB = Cat, new_BB = Destination)

        changes = masterChanges()

        
        # Redirect to edit_success page which easily allows the admin to return to the main admin panel or go directly to the admin/db page
        return templates.TemplateResponse("edit_success.html",
                                         {'request': request,
                                          'plaid_cat': Plaid_cat,
                                          'cat': Cat,
                                          'destination': Destination,
                                          'changes': changes})
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
    return templates.TemplateResponse("admin_edit.html",
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
async def user(request: Request,
               username: str = Depends(get_current_username)):
    resetUserTable()
    message = "The Users table was reset"
    return templates.TemplateResponse("reset_success.html",
                                     {'request': request,
                                      'message': message})
@app.post("/update_users")
async def update_users(update: dict):
    new = changePreferences(update)
    if new == 0:
        message = "Updated preferences successfully"
    return({"message": message})

# Route to display all changes in the change log table
@app.get("/admin/changelog")
async def view_changes(request: Request,
                       username: str = Depends(get_current_username)):
    changes = masterChanges(recent = False)
    return templates.TemplateResponse("master_changes.html",
                                     {'request': request,
                                      'changes': changes})