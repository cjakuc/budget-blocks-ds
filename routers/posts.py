from fastapi import APIRouter
from transactionhist import *
from DB.userDB import *
from census import *
import time

router = APIRouter()

# End point for the web backend to send transaction history objects and get back the same object w/ BB categories
@router.post("/transaction/", tags=["transaction"])
def transaction(trans: TransactionHistory):
    start_time = time.time()

    # Get the user ID
    user_id = trans.user_id

    # Get user preferences
    user_dict = getUser(user_id)

    # Recategorize the transactions
    request = trans.getCats(cats_dict=getUser(user_id))
    # request = trans.getCats(cats_dict=user_dict)

    # Retreive the census info for the right location and append it to the transactions JSON. Return it
    # request = census_totals(transactions=transactions, location=full_dict['location'], user_dict=user_dict)

    print("--- %s seconds ---" % (time.time() - start_time))

    request['request time in seconds'] = (time.time() - start_time)

    return request

@router.post("/census", tags=["census"])
async def user_census(census: Census):

    user_id = census.user_id

    user_dict = getUser(user_id)

    personalized_census = census.census_totals(user_dict=user_dict)

    return personalized_census

@router.post("/update_users", tags=["update_users"])
async def update_users(update: UpdatePreferences):
    new = update.changePreferences()
    if new == 0:
        message = "Updated preferences successfully"
    return({"message": message})