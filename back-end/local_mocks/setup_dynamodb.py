import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")

with open(os.path.join(os.path.dirname(__file__), '../data_polling/dynamodb/stockPriceTable.json'), 'r') as key_schema:
  table_definition = json.load(key_schema)
  response = dynamodb.create_table(**table_definition)

print(response)