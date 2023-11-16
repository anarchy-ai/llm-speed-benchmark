import requests
import csv
from io import StringIO
import json

def fetch_csv_data(url):
    response = requests.get(url)
    response.raise_for_status()

    csv_data = StringIO(response.text)
    csv_reader = csv.reader(csv_data, delimiter=',')
    data = list(csv_reader)

    return data

# get awesome-chatgpt-prompts data (https://github.com/f/awesome-chatgpt-prompts)
def get_acp_dataset():
    url = "https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv"
    data = fetch_csv_data(url)
    output = {}
    for i in range(len(data)):
        if i == 0:
            continue
        output[data[i][0]] = data[i][1]
    return output

