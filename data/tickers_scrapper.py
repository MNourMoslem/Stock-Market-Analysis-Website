import pandas as pd
import regex as re

data_dir = "./"
file_name = "5k_tickers.csv"
file_dir = data_dir + file_name

ptn = "\(\'[A-Za-z]+"

N = 5000
i = 0

tickers = [0] * N

with open(data_dir + "valid_tickers.csv", 'r') as file:
    file.readline()
    while i < N:
        line = file.readline()
        ticker = re.findall(ptn, line)
        if ticker:
            tickers[i] = ticker[0][2:]
            i+=1

df = pd.DataFrame(data = tickers ,columns=["tickers"])
df.to_csv(file_dir, index=False)

dfr = pd.read_csv(file_dir)

print(dfr)
