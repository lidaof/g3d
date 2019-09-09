import pickle
with open('test.dat', 'wb') as fout:
    pickle.dump({'test':'Hello Python!', 'test2': 2335.67}, fout)
    # fout.write(str(pickle.dumps('Hello Python!')))