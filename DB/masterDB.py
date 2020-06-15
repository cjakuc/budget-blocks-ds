import sqlite3 as sql
import pickle
import copy
from DB.DBhelper import dict_to_sql, sql_to_dict
import datetime
import psycopg2
from dotenv import load_dotenv
import os
# from main import cats_dict

pkl_file = open('./Pickle/cats_new.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

load_dotenv()

DBNAME = os.getenv("DBNAME", default="OOPS")
AUSER = os.getenv("AUSER", default="OOPS")
DBPASSWORD = os.getenv("DBPASSWORD", default="OOPS")
HOST = os.getenv("HOST", default="OOPS")

def resetMaster():
    """
    Function to create master table to store default categorization preferences
            Creates an "old" and a "new" table that are identical except for the value of is_old
    Inputs: None
    Output: None
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    # conn = sql.connect('BudgetBlocks.db')
    conn = psycopg2.connect(dbname=DBNAME, user=AUSER,
                            password=DBPASSWORD, host=HOST)

    # Create the Cursor object
    c = conn.cursor()

    # Delete the table if it exists
    c.execute("""
    DROP TABLE IF EXISTS master
    """)

    #Delete the changelogs table
    c.execute("""
    DROP TABLE IF EXISTS changelog
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
                    is_old_custom = True, c = c)

    # "Old" default entries in master table
    dict_to_sql(current_dict = cats_dict, is_master = True, 
                    is_old_custom = False, c = c)

    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()
    from DB.userDB import updateUsers
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
    conn = psycopg2.connect(dbname=DBNAME, user=AUSER,
                            password=DBPASSWORD, host=HOST)

    # Create the Cursor object
    c = conn.cursor()

    # Query the master table for the keys and save them to val
    query1 = "SELECT Key from master WHERE is_old is FALSE"

    # Query the master table for the strings that contain the lists of values separated by '/'
    query2 = "SELECT PLAID_Values from master WHERE is_old is FALSE"
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

    # Exception for if plaid_cats is not in old_BB
    if plaid_cat not in new_dict[old_cat]:
        raise HTTPException(status_code=500, detail=f"{plaid_cat} is not in {old_cat}")

    # Remove the plaid_cat from the old_cat's value list
    new_dict[old_cat].remove(plaid_cat)

    # Add the plaid_cat to the destination's value list
    new_dict[destination].append(plaid_cat)

    # Query the master table to check if there is a new dict there
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = psycopg2.connect(dbname=DBNAME, user=AUSER,
                            password=DBPASSWORD, host=HOST)

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
    Set is_old = TRUE
    """
    c.execute(replace_query)

    # Insert the newly made cats as the new dict
    dict_to_sql(current_dict = new_dict, is_master = True, 
                is_old_custom = False, c = c)

    
    # commit changes (if any)
    conn.commit()
    # close connection
    conn.close()

    from DB.userDB import updateUsers
    updateUsers(new_dict)
    
    return 0


def updateChangeLog(plaid_cat, old_BB, new_BB):
    """
    Function to store any changes to the master 
    """
    # Create the Connection object to the 'BudgetBlocks' DB
    conn = psycopg2.connect(dbname=DBNAME, user=AUSER,
                            password=DBPASSWORD, host=HOST)

    # Create the Cursor object
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS changelog(ID SERIAL PRIMARY KEY, Changes TEXT, Time TEXT);")

    conn.commit()

    message = f"{plaid_cat} was moved from {old_BB} to {new_BB}"

    # For whatever reason, when adding one column that's a string using the method we previous used it broke
    # repr() gives the "official" string representation and fixes issues with extra quotes, we think? It works
    # message = repr(message)

    # Get the current date and time to add to the change log
    current_time = str(datetime.datetime.now())

    # insertion_query = f"""
    # INSERT INTO changelog (Changes, Time)
    # VALUES
    # ({message})
    # """
    insertion_query = f"""
    INSERT INTO changelog (Changes, Time)
    VALUES
    {tuple((message, current_time))}
    """

    c.execute(insertion_query)

    conn.commit()

    conn.close()

    return 0

def masterChanges(recent: bool = True):
    """
    Function to get the 5 most recent changes, or all changes, in the change log table
    Inputs: recent - boolean corresponding to whether you want the 5 most recent changes
    Outputs: List of tuples that has the 5 most recent entries in the change log table
    """

    # Create the Connection object to the 'BudgetBlocks' DB
    conn = psycopg2.connect(dbname=DBNAME, user=AUSER,
                            password=DBPASSWORD, host=HOST)

    # Create the Cursor object
    c = conn.cursor()

    # Get the count of tables with the name "changelog"
    c.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'changelog');")

    check = c.fetchall()[0][0]

    changes = []
    #if the count is 0, then table does not exist, return that there are no changes
    if check == False:
        changes.append("No changes to display")
        return changes

    # If recent == True only get the 5 most recent changes, else get all of them
    if recent:
        query = """
        SELECT *
        FROM changelog
        ORDER BY id DESC
        LIMIT 5
        """
        
    else:
        query = """
        SELECT *
        FROM changelog
        ORDER BY id DESC
        """

    c.execute(query)

    temp = c.fetchall()

    # Clean up the changes
    for i in temp:
        changes.append([i[2],i[1].replace("_", " ")])

    conn.close()
        
    return changes