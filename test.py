from cats import cats_dict


total = 0

for i in cats_dict.keys():
    total = total + len(cats_dict[i])

print(total)


