from fastapi import FastAPI
from pydantic import BaseModel
from cats import cats_dict

# to run the app vvv
# uvicorn main:app --reload


# Instansiate FastAPI Class
# when running the model, "main" is the python file and "app"
# is the variable name that is holding the FastAPI class (main:app)
app = FastAPI()


# For reference
# plaid_cats = ["Bank Fees",
#               "Cash Advance",
#               "Community",
#               "Food and Drink".
#               "Healthcare",
#               "Interest",
#               "Payment",
#               "Recreation",
#               "Service",
#               "Shops",
#               "Tax",
#               "Transfer",
#               "Travel"]

# Go through sub-categories to find categories that has the word "housing" in it
# or something similar to housing

# to-do lists that holds specific sub-categorys
# Using something like str.contains()
cat_group_1_housing = []
cat_group_2_housing = []
cat_group_1_food = []
cat_group_2_food = []
cat_group_1_income = []
cat_group_2_income = []
cat_group_1_personal = []
cat_group_2_personal = []
cat_group_1_transportation = []
cat_group_2_transportation = []

class TransactionHistory(BaseModel):
    transactions: dict = None
    # default vars soon to be overwritten
    totals: dict = {"Income": 0.0,"Housing":0.0, "Food": 0.0, "Personal": 0.0, "Transportation": 0.0}


    def getCats(self):
    """
    Paramters: a TransactionHistory object
    Helper function to go through the transactions and categorize them
    Returns: list of categories of the transactions
    """
        cats = []

        # Index into each transaction dict
        for trans in self.transactions:

            # Index into the transaction categories and save them to variables
            plaid_cat1 = trans['transactions']['category'][0]
            # Dict could contain no sub-categories and may also contain index [2]
                # Would a try statement work here?
            plaid_cat2 = trans['transactions']['category'][1]

            # Need to figure out the edge case where there is only one sub-category and not two
            # Find the correct block to put the transaction in according to predetermined org
            if (plaid_cat1 in cat_group_1_income) & (plaid_cat2 in cat_group_2_income):
                cats.append("Income")
                self.totals['Income'] = self.totals["Income"] + trans['amount']

            if (plaid_cat1 in cat_group_1_housing) & (plaid_cat2 in cat_group_2_housing):
                cats.append("Housing")
                self.totals["Housing"] = self.totals["Housing"] + trans['amount']

            if (plaid_cat1 in cat_group_1_food) & (plaid_cat2 in cat_group_2_food):
                cats.append("Food")
                self.totals['Food'] = self.totals["Food"] + trans['amount']

            if (plaid_cat1 in cat_group_1_personal) & (plaid_cat2 in cat_group_2_personal):
                cats.append("Personal")
                self.totals['Personal'] = self.totals["Personal"] + trans['amount']

            if (plaid_cat1 in cat_group_1_transportation) & (plaid_cat2 in cat_group_2_transportation):
                cats.append("Transportation")
                self.totals['Transportation'] = self.totals["Transportation"] + trans['amount']

        return cats

@app.get("/")
def root():
    # Written as a dict but returns a json object
    return {"message": 'Hello World!'}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.post("/transaction/")
def transaction(trans: TransactionHistory):
    return trans