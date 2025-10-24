import json

with open('format_data_api/exchange.json', 'r') as f:
    data = json.load(f)

print(data['source'])
print(data['date'])
print(data['quotes'])