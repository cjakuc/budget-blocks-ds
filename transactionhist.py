from pydantic import BaseModel
from fastapi import HTTPException
import time


def reCatHelper(trans: dict, newCat: str):
    """
    Helper function to delete all the Plaid categories and replace with a single budget blocks category
    Parameters: a JSON object for a single transaction and the desired new budget blocks category
    Returns: the edited JSON object of a transaction
    """

    del trans['category']

    trans['category'] = []
    trans['category'].append(newCat)

    return trans

class TransactionHistory(BaseModel):
    full_dict:  dict = None

    # def __init__ (self, full_dict):
    #     self.full_dict = full_dict
    #     self.transactions = self.full_dict['transactions']
        

    def getCats(self, cats_dict: dict):
        """
        Helper function to go through the transactions and categorize them
        Paramters: a TransactionHistory object,
                   a dictionary whose keys are the budget blocks categories and the values are its corresponding Plaid categories
        Returns: a JSON object of all the transactions with the budget blocks categorizations
        """
        transactions = self.full_dict['transactions']
        # Index into each transaction dict
        for trans in transactions:
            
            # Need to be sure that category is the first key in the dictionary in the list trans['transactions]
            cat_list = trans['category']
            
            numb_of_cats = len(cat_list)
            
            print(cat_list)
            
            # Cash Advance is the only Plaid main category with no sub categories, and they all are remapped to "Income"
            if (numb_of_cats == 1) & (cat_list == ["Cash Advance"]):
                trans = reCatHelper(trans, "Income")
            elif (numb_of_cats == 1) & (cat_list != ["Cash Advance"]):
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

                            trans = reCatHelper(trans, key)

            # Custom error exception to tell us if there is a plaid category we didn't account for
                # Transportation is the only case where Plaid cat == Budget Blocks cat
            if (cat_list == trans['category']):
                raise HTTPException(status_code=500, detail=f"Contact the DS team: One of the categories from this list: {cat_list} is not accounted for")  
                     
        return transactions

# For the exceptions:
    # Ask Ryan Herr about best practice
        # Should we just print() our exceptions and return a JSON that says to contact DS
        # Otherwise the web team will get an "Internal Server Error" and may not know to contact us