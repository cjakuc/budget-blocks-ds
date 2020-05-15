from pydantic import BaseModel
from cats import cats_dict

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


# to-do lists that holds specific sub-categorys
cats_housing_main = []
cats_housing_sub = []
cats_food_main = []
cats_food_sub = []
cats_income_main = []
cats_income_sub = []
cats_personal_main = []
cats_personal_sub = []
cats_transportation_main = []
cats_transportation_sub = []

def reCatHelper(trans: dict, newCat: str):
    """
    Helper function to delete all the Plaid categories and replace with a single budget blocks category
    Parameters: a JSON object for a single transaction and the desired new budget blocks category
    Returns: the edited JSON object of a transaction
    """

    del trans['transactions'][0]['category']

    trans['transactions'][0]['category'] = []
    trans['transactions'][0]['category'].append(newCat)

    return trans

class TransactionHistory(BaseModel):
    transactions: list = None
    
    # default vars soon to be overwritten
    # totals: dict = {"Income": 0.0,"Housing":0.0, "Food": 0.0, "Personal": 0.0, "Transportation": 0.0}


    def getCats(self):
        """
        Helper function to go through the transactions and categorize them
        Paramters: a TransactionHistory object
        Returns: a JSON object of all the transactions with the budget blocks categorizations
        """
        
        # Index into each transaction dict
        for trans in self.transactions:
            
            numb_of_cats = []
            # Need to be sure that category is the first key in the dictionary in the list trans['transactions]
            cat_list = trans['transactions'][0]['category']
            
            numb_of_cats = len(cat_list)
            
            print(cat_list)

            if (numb_of_cats == 1):
                 # Index into the transaction categories and save them to variables
                plaid_cat1 = cat_list[0]
                if (plaid_cat1 in cats_income_main):
                    trans = reCatHelper(trans, "Income")
               
                if (plaid_cat1 in cats_housing_main):
                    trans = reCatHelper(trans, "Housing")
                    
                if (plaid_cat1 in cats_food_main):
                    trans = reCatHelper(trans, "Food")
                    
                if (plaid_cat1 in cats_personal_main):
                    trans = reCatHelper(trans, "Personal")
                    
                if (plaid_cat1 in cats_transportation_main):
                    trans = reCatHelper(trans, "Transportation")

            if (numb_of_cats >= 2):
                # Dict could contain no sub-categories and may also contain index [2]
                    # Would a try statement work here?
                plaid_cat2 = cat_list[1]

                # Need to figure out the edge case where there is only one sub-category and not two
                # Find the correct block to put the transaction in according to predetermined org
                if (plaid_cat2 in cats_income_sub):
                    trans = reCatHelper(trans, "Income")
                
                if (plaid_cat2 in cats_housing_sub):
                    trans = reCatHelper(trans, "Housing")
                    
                if (plaid_cat2 in cats_food_sub):
                    trans = reCatHelper(trans, "Food")
                    
                if (plaid_cat2 in cats_personal_sub):
                    trans = reCatHelper(trans, "Personal")
                    
                if (plaid_cat2 in cats_transportation_sub):
                     trans = reCatHelper(trans, "Transportation")
                    

        return self.transactions