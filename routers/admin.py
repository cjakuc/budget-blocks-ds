from DB.masterDB import *
from DB.userDB import *
import secrets
from mainhelp import *
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from fastapi import FastAPI, Request, status, Depends, HTTPException, APIRouter

router = APIRouter()

# Load the file from the path
load_dotenv()

AUSERNAME = os.getenv("AUSERNAME", default="OOPS")
PASSWORD = os.getenv("PASSWORD", default="OOPS")

templates = Jinja2Templates(directory="templates")

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security), tags=["admin"]):
    correct_username = secrets.compare_digest(credentials.username, AUSERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Basic"},
    )
    return credentials.username

@router.get("/admin", tags=["admin"])
def admin_main(request: Request,
               username: str = Depends(get_current_username)):
    return templates.TemplateResponse("admin_main.html",
                                     {'request': request})

@router.get("/admin/reset_master_confirmation", tags=["admin"])
def reset_master_confirmation(request: Request):
    return templates.TemplateResponse("master_confirmation.html",
                                     {'request': request})

@router.get("/admin/reset_user_confirmation", tags=["admin"])
def reset_user_confirmation(request: Request):
    return templates.TemplateResponse("user_confirmation.html",
                                     {'request': request})

@router.get("/admin/reset_master/", tags=["admin"])
def reset_master(request: Request, username: str = Depends(get_current_username)):
    resetMaster()
    message = "The master table was reset"
    return templates.TemplateResponse("reset_success.html",
                                     {'request': request,
                                      'message': message})

# Admin route to edit the master DB table through an interface
@router.get("/admin/edit_master", tags=["admin"])
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
@router.get("/admin/db", tags=["admin"])
async def db(request: Request,
             username: str = Depends(get_current_username)):
    master = masterPull()
    keys = list(master.keys())

    return templates.TemplateResponse("db.html",
                                     {'request': request,
                                      'keys': keys,
                                      'values': master})

# Route that allows us to reset/create the users table
@router.get("/admin/reset_user", tags=["admin"])
async def user(request: Request,
               username: str = Depends(get_current_username)):
    resetUserTable()
    message = "The Users table was reset"
    return templates.TemplateResponse("reset_success.html",
                                     {'request': request,
                                      'message': message})

# Route to display all changes in the change log table
@router.get("/admin/changelog", tags=["admin"])
async def view_changes(request: Request,
                       username: str = Depends(get_current_username)):
    changes = masterChanges(recent = False)
    return templates.TemplateResponse("master_changes.html",
                                     {'request': request,
                                      'changes': changes})