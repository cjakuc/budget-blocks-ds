import sqlite3 as sql
import pickle
import copy
# from main import cats_dict

pkl_file = open('cats_new.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

def resetMaster():
    """
    Function to create master tables to store default categorization preferences
            Creates an "old" and a "new" table that are identical except for the value of is_old
    Inputs: None
    Output: None
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = sql.connect('BudgetBlocks.db')

    # Create the Cursor object
    c = conn.cursor()

    # Delte the table if it exists
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

    for key in list(cats_dict.keys()):
        test = str(cats_dict[key])
        test = test.replace('], [', '/')
        test = test.replace('[[','')
        test = test.replace(']]','')
        test = test.replace("'","")
        insertion_query = f"""
        INSERT INTO master (Key, PLAID_Values, is_old)
        VALUES
        {tuple((key, test, True))}
        """
        c.execute(insertion_query)
        
    for key in list(cats_dict.keys()):
        test = str(cats_dict[key])
        test = test.replace('], [', '/')
        test = test.replace('[[','')
        test = test.replace(']]','')
        test = test.replace("'","")
        insertion_query = f"""
        INSERT INTO master (Key, PLAID_Values, is_old)
        VALUES
        {tuple((key, test, False))}
        """
        c.execute(insertion_query)

    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()

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

    # Create lists to store the keys and lists of values that correspond to them
    keys = []
    values = []

    # Query the master table for the keys and save them to val
    query = f"""
    SELECT Key
    from master
    WHERE is_old is FALSE
    """
    val = c.execute(query).fetchall()
    # Iterate through each key and append it to keys
    for i in val:
        keys.append(i[0])

    # Query the master table for the strings that contain the lists of values separated by '/'
    query2 = f"""
    SELECT PLAID_Values
    from master
    WHERE is_old is FALSE
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
    WHERE is_old is TRUE
    """
    c.execute(delete_query)

    # Make the current new, old
    replace_query = """
    Update master
    Set is_old = replace(is_old, FALSE, TRUE) 
    """
    c.execute(replace_query)

    # Insert the new, new
    for key in list(new_dict.keys()):
        test = str(new_dict[key])
        test = test.replace('], [', '/')
        test = test.replace('[[','')
        test = test.replace(']]','')
        test = test.replace("'","")
        insertion_query = f"""
        INSERT INTO master (Key, PLAID_Values, is_old)
        VALUES
        {tuple((key, test, False))}
        """
        c.execute(insertion_query)

    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()

    return 0
