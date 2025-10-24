import json

with open('format_data_api/list_ticket.json', 'r') as f:
    data = json.load(f)

for item in data['data']:
    print(item['name'])
    print(item['ticker'])
    print(item['has_intraday'])
    print(item['has_eod'])
    print(item['stock_exchange']['name'])
    print(item['stock_exchange']['acronym'])
    print(item['stock_exchange']['mic'])
    print('--------------------------------')
    break