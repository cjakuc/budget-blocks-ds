from fastapi import HTTPException
import sqlite3 as sql


def dict_to_sql(current_dict: dict, is_master: bool, is_old_custom: int, c, user_id: int = None):
    """
    Function to take a dictionary and write it to either the master or users tables
    Inputs: current_dict - The dictionary to input into the table
            is_master - Boolean stating whether or not the table is master
            is_old_custom - Integer (1 or 0) for whether the master dict is old or the users dict is custom
            c - cursor object to execute the query
            user_id - Integer user ID
    Outputs: None
    """
    # Raise exception if is_old_custom != 0 or 1
    if (is_old_custom != 0) & (is_old_custom != 1):
        raise HTTPException(status_code=500, detail=f"In dict_to_sql, is_old_custom was not 0 or 1")
    
    if is_master:
        for key in list(current_dict.keys()):
            test = str(current_dict[key])
            test = test.replace('], [', '/')
            test = test.replace('[[','')
            test = test.replace(']]','')
            test = test.replace("'","")
            insertion_query = f"""
            INSERT INTO master (Key, PLAID_Values, is_old)
            VALUES
            {tuple((key, test, is_old_custom))}
            """
            c.execute(insertion_query)

    else:
        # Raise exception if is_master == 0 and user_id == None
        if user_id == None:
            raise HTTPException(status_code=500, detail=f"In dict_to_sql, no user_id was passed when is_master was 0")

        for key in list(current_dict.keys()):
            test = str(current_dict[key])
            test = test.replace('], [', '/')
            test = test.replace('[[','')
            test = test.replace(']]','')
            test = test.replace("'","")
            insertion_query = f"""
            INSERT INTO users (user_id, Key, PLAID_Values, is_custom)
            VALUES
            {tuple((user_id, key, test, is_old_custom))}
            """
            c.execute(insertion_query)

    return 0
 
def sql_to_dict(query1: str, query2: str, c):
    """
    Function to convert SQL table into a dictionary
    Inputs: query1 - query to get the keys
            query2 - query to get the values
            c - cursor object
    Outputs: new_dict - dictionary of keys and values
    """
    keys = []
    val = c.execute(query1).fetchall()
    # Iterate through each key and append it to keys
    for i in val:
        keys.append(i[0])

    values = []
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

    return new_dict