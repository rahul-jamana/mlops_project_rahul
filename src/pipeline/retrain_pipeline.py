import pandas as pd
import os


def retrain():
    old = pd.read_csv("data/processed/train.csv")
    new = pd.read_csv("data/new/new_data.csv")

    new = new.dropna()

    df = pd.concat([old, new])
    df.to_csv("data/processed/train.csv", index=False)

    os.system("python src/model/train.py")


if __name__ == "__main__":
    retrain()
