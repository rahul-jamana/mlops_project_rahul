import os


def run_pipeline():
    os.system("python src/data/preprocess.py")
    os.system("python src/model/train.py")


if __name__ == "__main__":
    run_pipeline()
