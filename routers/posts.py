from fastapi import APIRouter
from transactionhist import *
from DB.userDB import *
from census import *
import time

router = APIRouter()

# End point for the web backend to send transaction history objects and
# get back the same object w/ BB categories
@router.post("/transaction/", tags=["transaction"])
def transaction(trans: TransactionHistory):
    start_time = time.time()

    # Get the user ID
    user_id = trans.user_id

    # Get user preferences
    user_dict = getUser(user_id)

    # Recategorize the transactions
    request = trans.getCats(cats_dict=getUser(user_id))

    print("--- %s seconds ---" % (time.time() - start_time))

    request['request time in seconds'] = (time.time() - start_time)

    return request

# End point for the web team to send a user's location and user id, and
# receive the average census expenditures of people in the nearest city
@router.post("/census", tags=["census"])
async def user_census(census: Census):

    # Get the user ID
    user_id = census.user_id

    # Get the user's preferences
    user_dict = getUser(user_id)

    # Create the personalized census dictionary
    personalized_census = census.census_totals(user_dict=user_dict)

    return personalized_census

# End point for the web team to edit a user's preferences by switching a
# specific plaid category from one BB category to another
@router.post("/update_users", tags=["update_users"])
async def update_users(update: UpdatePreferences):
    new = update.changePreferences()
    if new == 0:
        message = "Updated preferences successfully"
    return({"message": message})

# Test version of the transaction endpoint where "Income" is a seperate key from the rest of the totals
@router.post("/transaction_test/", tags=["transaction"])
def transaction(trans: TransactionHistory):
    start_time = time.time()

    # Get the user ID
    user_id = trans.user_id

    # Get user preferences
    user_dict = getUser(user_id)

    # Recategorize the transactions
    request = trans.getCats(cats_dict=getUser(user_id))

    # Create a new seperate key for income to test Adam's solution and delete
    # the old one
    request['Income'] = request['totals']['Income']
    del request['totals']['Income']

    print("--- %s seconds ---" % (time.time() - start_time))

    request['request time in seconds'] = (time.time() - start_time)

    return request

@router.post("/reset_user", tags=['reset_user'])
def reset_user(user: User):
    message = user.reset_user_cats()

    return({"message": message})

@router.post("/delete_user", tags=['delete_user'])
def delete_user(user: User):
    message = user.delete_user()

    return({"message": message})