from copy import deepcopy


def DictHTML(Dict: dict):
    """
    Function that formats the values of our master dict so they can be manipulatedly more easily in the HTML files
            (Spaces were breaking it because spaces can't be in a URL)
    Inputs: Dict - a dictionary (master table before HTML formatting)
    Outputs: the same dictionary with the items of a list joined using "_AND_" and the spaces replaced with "_" (Dict)
           : a copy of the same dictionary with the items of a list joined using " AND " (master) for displaying
    """
    # VERY IMPORTANT: regularly copying a dict doesn't create a new object, it
    # creates a new reference to the original object, so we had to do this
    master = deepcopy(Dict)

    # iterate through keys
    for key in list(Dict.keys()):
        # iterate through words from a specified key
        for w, i in enumerate(Dict[key]):
            # If the list only contains one word
            if len(i) == 1:
                # Pull the word out of the list
                for v in i:
                    # set that word to a variable
                    x = v
                    # The index of that list is now a string of the word that
                    # was inside the list
                    Dict[key][w] = x
                    master[key][w] = x
            # If the list contains two words
            elif len(i) == 2:
                # Pull the words out of the list
                for num, v in enumerate(i):
                    # Checks if its the first iteration
                    if num == 0:
                        # create x variable with the first word
                        x = v
                    # Checks if it is the second iteration
                    if num == 1:
                        # append the second word to the first word
                        # and add the word AND inbetween each word
                        y = x + " AND " + v
                        x = x + "_AND_" + v
                        Dict[key][w] = x
                        master[key][w] = y

    # Iterate through each key
    for key in list(Dict.keys()):
        # Iterate through a list for the specified key
        for w, i in enumerate(Dict[key]):
            # Create a change variable that holds the current string
            change = Dict[key][w]
            # Checks if the word is a string
            if isinstance(change, str):
                # replace each space in the word with underscores
                Dict[key][w] = change.replace(' ', '_')

    return Dict, master
