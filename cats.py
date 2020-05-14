import pickle

pkl_file = open('cats.pkl', 'rb')
cats_dict = pickle.load(pkl_file)
pkl_file.close()

print(cats_dict.keys())