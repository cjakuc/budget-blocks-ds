from fastapi import FastAPI, Request, status, Depends, HTTPException
from pydantic import BaseModel
from transactionhist import *
import pickle
import time
from masterDB import *
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import copy
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from dotenv import load_dotenv
import os
from os.path import join, dirname

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


def DictHTML(Dict: dict):
    """
    Function that formats the values of our master dict so they can be manipulatedly more easily in the HTML files
            (Spaces were breaking it because spaces can't be in a URL)
    Inputs: a dictionary
    Outputs: the same dictionary with the items of a list joined using "_AND_" and the spaces replaced with "_" (Dict)
           : a copy of the same dictionary with the items of a list joined using " AND " (master)
    """
    # VERY IMPORTANT: regularly copying a dict doesn't create a new object, it creates a new reference to the original object, so we had to do this
    master = copy.deepcopy(Dict)

    # iterate through keys
    for key in list(Dict.keys()):
        # iterate through words from a specified key
        for w,i in enumerate(Dict[key]):
            # If the list only contains one word
            if len(i) == 1:
                # Pull the word out of the list
                for v in i:
                    # set that word to a variable
                    x = v
                    # The index of that list is now a string of the word that was inside the list
                    Dict[key][w] = x
                    master[key][w] = x
            # If the list contains two words
            elif len(i) == 2:
                # Pull the words out of the list
                for num, v in enumerate(i):
                    # Checks if its the first iteration
                    if num == 0:
                        # create x variable with the first word
                        x = v
                    # Checks if it is the second iteration
                    if num == 1:
                        # append the second word to the first word
                        # and add the word AND inbetween each word
                        y = x + " AND " + v
                        x = x + "_AND_" + v
                        Dict[key][w] = x
                        master[key][w] = y
    
    # Iterate through each key
    for key in list(Dict.keys()):
        # Iterate through a list for the specified key
        for w,i in enumerate(Dict[key]):
            # Create a change variable that holds the current string
            change = Dict[key][w]
            # Checks if the word is a string
            if type(change) == str:
                # replace each space in the word with underscores
                Dict[key][w] = change.replace(' ', '_')

    return Dict, master

app = FastAPI()


templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    # Written as a dict but returns a json object
    return {"message": 'Hello World!'}

# End point for the web backend to send transaction history objects and get back the same object w/ BB categories
@app.post("/transaction/")
def transaction(full_dict: dict):
    start_time = time.time()
    trans = TransactionHistory(full_dict=full_dict)
    request = trans.getCats(cats_dict=masterPull())
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
    values = []
    for key in keys:
        values.append(master[key])

    return templates.TemplateResponse("db.html",
                                     {'request': request,
                                      'keys': keys,
                                      'values': values})







# Check if we accidentaly didn't drop anything when messing with the dicts homie

# Maybe move function to another py file
