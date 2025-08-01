import pandas as pd


def main():
  file = "C:\\Users\\36943\\Documents\\Tokens in each source file.csv"
  df = pd.read_csv(file)
  df = df[(df["Company"] == "Apache") & (df["Language"] == "Java")]
  values = df["value"].tolist()
  print(values)


if __name__ == '__main__':
  main()
