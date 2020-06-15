from pydantic import BaseModel
from fastapi import HTTPException
from pydantic import BaseModel

def reCatHelper(trans: dict, newCat: str, totals: dict):
    """
    Helper function to retitle the Plaid categories from 'category' to 'plaid_category' and add a single budget blocks category, 'budget_blocks_category'
    Parameters: a JSON object for a single transaction and the desired new budget blocks category
    Returns: the edited JSON object of a transaction
    """
    temp = trans['category'].copy()
    trans['plaid_category'] = temp
    # [:] Means everything in the list
    del trans['category']

    trans['budget_blocks_category'] = []
    trans['budget_blocks_category'].append(newCat)

    # Increment totals
    totals[newCat] += trans['amount']
     
    return trans

class TransactionHistory(BaseModel):
    transactions:  list
    user_id: int

    # Example JSON for the transaction request
    class Config:
        schema_extra = {
            "example": {
                "transactions": [
                    {
                        "account_id": "k9VvjL1Eq3Cnk8gaQXDXt3aRVe7DaGiWekXgz",
                        "account_owner": 0,
                        "amount": 25,
                        "authorized_date": 0,
                        "category": [
                        "Payment",
                        "Credit Card"
                        ],
                        "category_id": "16001000",
                        "date": "2020-05-15",
                        "iso_currency_code": "USD",
                        "location": {
                        "address": 0,
                        "city": 0,
                        "country": 0,
                        "lat": 0,
                        "lon": 0,
                        "postal_code": 0,
                        "region": 0,
                        "store_number": 0
                        },
                        "name": "CREDIT CARD 3333 PAYMENT *//",
                        "payment_channel": "other",
                        "payment_meta": {
                        "by_order_of": 0,
                        "payee": 0,
                        "payer": 0,
                        "payment_method": 0,
                        "payment_processor": 0,
                        "ppd_id": 0,
                        "reason": 0,
                        "reference_number": 0
                        },
                        "pending": False,
                        "pending_transaction_id": 0,
                        "transaction_code": 0,
                        "transaction_id": "47E1jBQLoNhA6ajvnLeLCX4NwvKQmnFd7wQ8K",
                        "transaction_type": "special",
                        "unofficial_currency_code": 0
                    }
                ],
                "user_id": 1
            }
            }

    def getCats(self, cats_dict: dict):
        """
        Function to go through the transactions and categorize them
        Paramters: a TransactionHistory object,
                   a dictionary whose keys are the budget blocks categories and the values are its corresponding Plaid categories
        Returns: a JSON object of all the transactions with the budget blocks categorizations
        """
        transactions = self.transactions
        # Dictionary to store the totals of each BB category
        totals = {}
        # Create a key in totals for each BB category so we can do += later
        for cat in list(cats_dict.keys()):
            totals[cat] = 0

        # Index into each transaction dict
        for trans in transactions:
            
            # Need to create a copy so that it keeps the original value and doesn't get updated by getCats
            cat_list = trans['category'].copy()
            
            numb_of_cats = len(cat_list)
            
            # print(cat_list)
            
            # Cash Advance is the only Plaid main category with no sub categories, and they all are remapped to "Income"
            if (numb_of_cats == 1) & (cat_list == ["Cash Advance"]):
                trans = reCatHelper(trans, "Income", totals)
            elif (numb_of_cats == 1) & (cat_list == ["Payment"]):
                trans = reCatHelper(trans, "Debt", totals)
            elif (numb_of_cats == 1) & (cat_list != ["Cash Advance"] or cat_list != ['Payment']):
                raise HTTPException(status_code=500, detail=f"Contact the DS team: There was only a single category, {cat_list}, and it was not Cash Advance")


            elif (numb_of_cats >= 2):
                # Making it so cat_list doesn't include the first index (main category from Plaid)
                cat_list_sliced = cat_list[1:]
                dupl_test = 0
                # Iterate through the lists in the dict, check if cat_list is in each list, and use reCatHelper to change the category
                for key in list(cats_dict.keys()):
                    for i in cats_dict[key]:
                        if cat_list_sliced == i:
                            dupl_test += 1
                            # Custom exception to report if a cat_list is in 2 or more cat_dicts lists
                            if dupl_test >= 2:
                                raise HTTPException(status_code=500, detail=f"Contact the DS team: A cat_list, {cat_list_sliced}, is in two or more cat_dicts lists, {trans['transactions'][0]['category'][0]} and {key}")

                            trans = reCatHelper(trans, key, totals)

            # Custom error exception to tell us if there is a plaid category we didn't account for
                # Transportation is the only case where Plaid cat == Budget Blocks cat
            if ('category' in trans):
                raise HTTPException(status_code=500, detail=f"Contact the DS team: One of the categories from this list: {cat_list} is not accounted for")  

        # Putting the transactions back into the dict so match what was plugged in
        temp_dict = {"transactions": transactions,
                    "user_id": self.user_id,
                    "totals": totals}

        return temp_dict