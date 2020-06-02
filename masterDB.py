import sqlite3 as sql
import pickle
import copy
from DBhelper import dict_to_sql, sql_to_dict
# from main import cats_dict

pkl_file = open('cats_new.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

def resetMaster():
    """
    Function to create master table to store default categorization preferences
            Creates an "old" and a "new" table that are identical except for the value of is_old
    Inputs: None
    Output: None
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = sql.connect('BudgetBlocks.db')

    # Create the Cursor object
    c = conn.cursor()

    # Delete the table if it exists
    c.execute("""
    DROP TABLE IF EXISTS master
    """)

    # Create table
    c.execute("""
    CREATE TABLE master
    (Key TEXT,
    PLAID_Values TEXT,
    is_old BOOLEAN)
    """)    

    # Check if table is empty
    empty_query = """
    SELECT count(*)
    FROM master
    """
    
    # "New" default entries in master table
    dict_to_sql(current_dict = cats_dict, is_master = True, 
                    is_old_custom = 1, c = c)

    # "Old" default entries in master table
    dict_to_sql(current_dict = cats_dict, is_master = True, 
                    is_old_custom = 0, c = c)

    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()
    from userDB import updateUsers
    updateUsers(cats_dict)

    return 0

def masterPull():
    """
    Function to pull the default categorization preferences from the database and return them in the proper format
    Inputs: Boolean variable old controls whether you pull the most up to date dict or the old version
    Outputs: Dictionary of default categorization preferences where each key is a Budget Blocks category and the values are 
             the Plaid categories that belong to the Budget Block categories
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = sql.connect('BudgetBlocks.db')

    # Create the Cursor object
    c = conn.cursor()

    # Query the master table for the keys and save them to val
    query1 = f"""
    SELECT Key
    from master
    WHERE is_old is 0
    """

    # Query the master table for the strings that contain the lists of values separated by '/'
    query2 = f"""
    SELECT PLAID_Values
    from master
    WHERE is_old is 0
    """
    new_dict = sql_to_dict(query1 = query1, query2 = query2, c = c)

    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()

    # Return the new dictionary
    return new_dict

def updateMaster(old_cat, plaid_cat, destination):
    """
    Function that updates the master table. If there is only an old dict, it inserts the new one.
            If there is a current old and new, it deletes the old, turns the current new to old, and inserts the new.
    Inputs: old_cat - the old BB category of the plaid category that needs to be remapped
          : plaid_cat - the plaid category that needs to be remapped
          : destination - the new BB category of the plaid category
    """

    # Reformat the plaid_cat back into a comma separated list
    if "_AND_" in plaid_cat:
        plaid_cat = plaid_cat.split("_AND_")
    else:
        plaid_cat = [plaid_cat]

    for i, v in enumerate(plaid_cat):
        plaid_cat[i] = v.replace('_', ' ')

    # Pull the current defaults
    old_dict = copy.deepcopy(masterPull())
    new_dict = copy.deepcopy(masterPull())

    # Remove the plaid_cat from the old_cat's value list
    new_dict[old_cat].remove(plaid_cat)

    # Add the plaid_cat to the destination's value list
    new_dict[destination].append(plaid_cat)

    # Query the master table to check if there is a new dict there
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = sql.connect('BudgetBlocks.db')

    # Create the Cursor object
    c = conn.cursor()

    # Delete the old
    delete_query = """
    DELETE
    FROM master
    WHERE is_old is 1
    """
    c.execute(delete_query)

    # Make the current new, old
    replace_query = """
    Update master
    Set is_old = replace(is_old, 0, 1) 
    """
    c.execute(replace_query)

    # Insert the newly made cats as the new dict
    dict_to_sql(current_dict = new_dict, is_master = True, 
                is_old_custom = 0, c = c)

    
    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()

    from userDB import updateUsers
    updateUsers(new_dict)
    
    return 0
