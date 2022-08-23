import pickle

with open("b.obj", "rb") as f:
    b = pickle.load(f)
b.run()
