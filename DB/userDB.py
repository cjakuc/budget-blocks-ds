from DB.masterDB import *
import sqlite3 as sql
import pickle
import copy
from DB.DBhelper import sql_to_dict, dict_to_sql
from fastapi import HTTPException

def resetUserTable():
    """
    Function to create user table to store custom categorization preferences
    Inputs: None
    Output: None
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = sql.connect('BudgetBlocks.db')

    # Create the Cursor object
    c = conn.cursor()

    # Delete the table if it exists
    c.execute("""
    DROP TABLE IF EXISTS users
    """)

    # Create table
    c.execute("""
    CREATE TABLE users
    (user_id INTEGER, 
    Key TEXT,
    PLAID_Values TEXT,
    is_custom BOOLEAN)
    """)

    conn.commit()

    conn.close()

    return 0

def getUser(user_id):
    """
    Function that checks if the user is currently in the users table
        If not in the table: Pulls from master to create their preferences and returns them as a dict
        If in the table, pulls their preferences and returns them as a dict
    Inputs: Unique user id
    Output: A dict of the user's preferences
    """
    conn = sql.connect('BudgetBlocks.db')

    c = conn.cursor()

    find_user = (f"""
    SELECT *
    FROM users
    WHERE user_id is {user_id}
    """)

    a_user = c.execute(find_user).fetchall()

    # if the user already exists in the DB, grab whats currently there
    if a_user != []:
        # Query the master table for the keys and save them to val
        query1 = f"""
        SELECT Key
        from users
        WHERE user_id is {user_id}
        """

        # Query the master table for the strings that contain the lists of values separated by '/'
        query2 = f"""
        SELECT PLAID_Values
        from users
        WHERE user_id is {user_id}
        """

        new_dict = sql_to_dict(query1 = query1, query2 = query2, c = c)

        conn.close()
        
        return new_dict
    
    # If the user doesn't exist in the DB, provide it the master dict
    else:
        current_dict = masterPull()
        dict_to_sql(current_dict = current_dict, is_master = False, 
                    is_old_custom = 0, c = c, user_id = user_id) 

        conn.commit()

        conn.close()

        return current_dict

def updateUsers(new_dict: dict):
    """
    Function that takes in the newest default preferences, and replaces the preferences
        of users that are using the defaults
    Inputs: Dictionairy of new defaults
    Outputs: None
    """
    conn = sql.connect('BudgetBlocks.db')

    c = conn.cursor()

    modify_check = """
    SELECT DISTINCT user_id
    FROM users
    WHERE is_custom is 0
    """
    modified = c.execute(modify_check).fetchall()
    if modified == []:
        return 0
    user_ids = []
    for tup in modified:
        for value in tup:
            user_ids.append(value)

    delete_query = """
    DELETE
    FROM users
    WHERE is_custom is 0
    """
    c.execute(delete_query)

    for user in user_ids:
        dict_to_sql(current_dict = new_dict, is_master = False, 
                    is_old_custom = 0, c = c, user_id = user)

    conn.commit()
    conn.close()
    
    return 0

def changePreferences(update: dict):
    """
    Function to update a user's ctaegorical preferences in the users table
    Inputs: update - dictionary containing:
                plaid_cats - the plaid_cats to be moved
                old_BB - the Budget Blocks category where the plaid cats currently are
                new_BB - the Budget Blocks category where the plaid cats will be moved to
                user_id - the user ID
    Outputs: None
    """
    # If the user doesn't already exist then it breaks
    plaid_cats = update['plaid_cats']
    old_BB = update['old_BB']
    new_BB = update['new_BB']
    user_id = update['user_id']

    conn = sql.connect('BudgetBlocks.db')

    c = conn.cursor()
    
    keys = []
    values = []
    # Query the users table for the keys and save them to val
    query1 = f"""
    SELECT Key
    from users
    WHERE user_id is {user_id}
    """

    # Query the users table for the strings that contain the lists of values separated by '/'
    query2 = f"""
    SELECT PLAID_Values
    from users
    WHERE user_id is {user_id}
    """
    
    new_dict = sql_to_dict(query1 = query1, query2 = query2, c = c)

    # Exception for if plaid_cats is not in old_BB
    if plaid_cats not in new_dict[old_BB]:
        raise HTTPException(status_code=500, detail=f"{plaid_cats} is not in {old_BB} for user {user_id}")
    
    else:
        # Remove the plaid_cat from the old_cat's value list
        new_dict[old_BB].remove(plaid_cats)

        # Add the plaid_cat to the destination's value list
        new_dict[new_BB].append(plaid_cats)
        
    delete_query = f"""
    DELETE
    FROM users
    WHERE user_id is {user_id}
    """

    c.execute(delete_query)

   # Insert the new
    dict_to_sql(current_dict = new_dict, is_master = False,
                user_id = user_id, c = c, is_old_custom = 1)

    conn.commit()
    conn.close()

    return 0