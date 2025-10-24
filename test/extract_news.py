import os
from dotenv import load_dotenv

load_dotenv()

symbols = os.getenv("SYMBOLS_EOD")
for symbol in symbols.split(','):
    print(symbol)
    