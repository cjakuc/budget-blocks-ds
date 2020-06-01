from masterDB import *
import sqlite3 as sql
import pickle
import copy

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
         # Create lists to store the keys and lists of values that correspond to them
        keys = []
        values = []
         # Query the master table for the keys and save them to val
        query = f"""
        SELECT Key
        from users
        WHERE user_id is {user_id}
        """
        val = c.execute(query).fetchall()
        # Iterate through each key and append it to keys
        for i in val:
            keys.append(i[0])

        # Query the master table for the strings that contain the lists of values separated by '/'
        query2 = f"""
        SELECT PLAID_Values
        from users
        WHERE user_id is {user_id}
        """
        vals = c.execute(query2).fetchall()
        # Iterate through the string values and do some splitting to turn them into the correct list of lists format
        for i in vals:
            words = i[0]
            words =  words.split('/')
            for i in range(len(words)):
                words[i] = words[i].split(', ', 1)
            
            values.append(words)
        
        # Create a new dictionary and populate it with the keys and values we've extracted and formatted
        new_dict = {}
        for i, key in enumerate(keys):
            new_dict[key] = values[i]

        conn.close()
        
        return new_dict
    
    # If the user doesn't exist in the DB, provide it the master dict
    else:
        current_dict = masterPull()
        for key in list(current_dict.keys()):
            test = str(current_dict[key])
            test = test.replace('], [', '/')
            test = test.replace('[[','')
            test = test.replace(']]','')
            test = test.replace("'","")
            insertion_query = f"""
            INSERT INTO users (user_id, Key, PLAID_Values, is_custom)
            VALUES
            {tuple((user_id, key, test, 0))}
            """
            c.execute(insertion_query)

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
        for key in list(new_dict.keys()):
            test = str(new_dict[key])
            test = test.replace('], [', '/')
            test = test.replace('[[','')
            test = test.replace(']]','')
            test = test.replace("'","")
            insertion_query = f"""
            INSERT INTO users (user_id ,Key, PLAID_Values, is_custom)
            VALUES
            {tuple((user, key, test, 0))}
            """
            c.execute(insertion_query)
    
    conn.commit()
    conn.close()
    
    return 0


def changePreferences(expected: dict):
    """
    
    """
    plaid_cats = expected['plaid_cats']
    old_BB = expected['old_BB']
    new_BB = expected['new_BB']
    user_id = expected['user_id']

    conn = sql.connect('BudgetBlocks.db')

    c = conn.cursor()
    
    keys = []
    values = []
    # Query the master table for the keys and save them to val
    query = f"""
    SELECT Key
    from users
    WHERE user_id is {user_id}
    """
    val = c.execute(query).fetchall()
    # Iterate through each key and append it to keys
    for i in val:
        keys.append(i[0])

    # Query the master table for the strings that contain the lists of values separated by '/'
    query2 = f"""
    SELECT PLAID_Values
    from users
    WHERE user_id is {user_id}
    """
    vals = c.execute(query2).fetchall()
    # Iterate through the string values and do some splitting to turn them into the correct list of lists format
    for i in vals:
        words = i[0]
        words =  words.split('/')
        for i in range(len(words)):
            words[i] = words[i].split(', ', 1)
        
        values.append(words)
    
    # Create a new dictionary and populate it with the keys and values we've extracted and formatted
    new_dict = {}
    for i, key in enumerate(keys):
        new_dict[key] = values[i]

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
    for key in list(new_dict.keys()):
        test = str(new_dict[key])
        test = test.replace('], [', '/')
        test = test.replace('[[','')
        test = test.replace(']]','')
        test = test.replace("'","")
        insertion_query = f"""
        INSERT INTO users (user_id ,Key, PLAID_Values, is_custom)
        VALUES
        {tuple((user_id, key, test, 1))}
        """
        c.execute(insertion_query)

    conn.commit()
    conn.close()

    return 0