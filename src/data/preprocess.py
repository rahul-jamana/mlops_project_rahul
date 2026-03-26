import pandas as pd


def preprocess():
    df = pd.read_csv("data/raw/student_scores.csv")

    # Remove duplicates and missing values (prevents repeated data from inflating training)
    df = df.drop_duplicates().dropna().reset_index(drop=True)
    df["hours_squared"] = df["Hours"] ** 2

    df.to_csv("data/processed/train.csv", index=False)


if __name__ == "__main__":
    preprocess()
