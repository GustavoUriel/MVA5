import pandas as pd
from app.scripts.files import findFileType

def test_files():
    paths = [
        "instance/taxonomy.csv",
        "instance/patients.csv",
        "instance/bracken.csv",
        "instance/patients -erer llc.csv",
    ]

    for p in paths:
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"{p}: Error reading file: {e}")
            continue

        try:
            t = findFileType(df)
        except Exception as e:
            t = f"Error during detection: {e}"

        print(f"{p}: {t}")


if __name__ == "__main__":
    test_files()
