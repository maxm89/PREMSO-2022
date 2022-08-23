import pickle
import classB

b = classB.B()
with open("b.obj",'wb') as f:
    pickle.dump(b,f)