from fastapi import FastAPI
from pydantic import BaseModel
from transactionhist import *
import pickle
import time

pkl_file = open('cats_new.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

# to run the app vvv
# uvicorn main:app --reload


# Instansiate FastAPI Class
# when running the model, "main" is the python file and "app"
# is the variable name that is holding the FastAPI class (main:app)
app = FastAPI()

@app.get("/")
def root():
    # Written as a dict but returns a json object
    return {"message": 'Hello World!'}


# @app.post("/transaction/")
# def transaction(trans: TransactionHistory):
#     start_time = time.time()
#     request = trans.getCats(cats_dict=cats_dict)
#     print("--- %s seconds ---" % (time.time() - start_time))
#     return request

@app.post("/transaction/")
def transaction(full_dict: dict):
    start_time = time.time()
    trans = TransactionHistory(full_dict=full_dict)
    request = trans.getCats(cats_dict=cats_dict)
    print("--- %s seconds ---" % (time.time() - start_time))
    return request