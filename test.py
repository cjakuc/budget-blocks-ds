from cats import cats_dict

# print(cats_dict['Community'])

housing = []
for i in list(cats_dict.keys()):
    for v in cats_dict[i]:
        if "Housing" in v or "Rent" in v:
            housing.append([i,v])

print(housing)


# ["Housing", "Rent", 'Water','House','Mortage']