import sqlite3 as sql
import pickle
# from main import cats_dict

pkl_file = open('cats_new.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

def createMaster():
    """
    Function to create master table to store default categorization preferences
    Inputs: None
    Output: None
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = sql.connect('BudgetBlocks.db')

    # Create the Cursor object
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS master
    (index_col SERIAL PRIMARY KEY,
    Key TEXT,
    PLAID_Values TEXT)
    """)    

    # Check if table is empty
    empty_query = """
    SELECT count(*)
    FROM master
    """
    empty_check = c.execute(empty_query).fetchall()
    if empty_check == [(0,)]:
        for key in list(cats_dict.keys()):
            test = str(cats_dict[key])
            test = test.replace('], [', '/')
            test = test.replace('[[','')
            test = test.replace(']]','')
            test = test.replace("'","")
            insertion_query = f"""
            INSERT INTO master (Key, PLAID_Values)
            VALUES
            {tuple((key, test))}
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
    Inputs: None
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
    query = """
    SELECT Key
    from master
    """
    val = c.execute(query).fetchall()
    # Iterate through each key and append it to keys
    for i in val:
        keys.append(i[0])

    # Query the master table for the strings that contain the lists of values separated by '/'
    query2 = """
    SELECT PLAID_Values
    from master
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