import pickle

if __name__ == "__main__":
    with open("./out/100000_110000_crawled.pickle", 'rb') as f:
        datas = pickle.load(f)
        print(datas)