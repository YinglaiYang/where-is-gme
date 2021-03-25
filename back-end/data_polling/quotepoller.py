import datetime
import requests
import schedule
import aiohttp
import asyncio
import boto3
import os

from decimal import Decimal

async def update_timezone():
    ''' 
    Calls Timezone.API for the timezone offset.
    '''
    r = requests.get('https://timezoneapi.io/api/timezone/?America/New_York&token={api_key}'.format(api_key=os.getenv('TIMEZONEAPI_API_KEY')))
    timezone_delta_utc_to_eastern = r.json()['data']['datetime']['offset_seconds']
    print(timezone_delta_utc_to_eastern)

    await asyncio.sleep(1800)

async def get_price_from_alphavantage_and_store(api_key, ticker):
    '''
    Performs a REST request to Alpha Vantage to get the current quote of GME. Implemented as an asynchronous
    call of *aiohttp* with expectation of a better performance then a call using *requests*.
    '''
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={0}&apikey={1}'.format(ticker, api_key)) as response:
            av_response_json = await response.json()
            return av_response_json

async def quote_routine(stockPriceTable):
    '''
    The routine that actually schedules the polling calls to Alpha Vantage.
    Changes polling interval between trading hours and non-trading hours.
    Extended hours are polled at same speed as normal trading hours.
    '''
    # Configurations
    ticker = 'GME'
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    polling_interval_trading_hours  = 60.0 / 70.0 #[s]
    polling_interval_inactive_hours = 10          #[s] 

    trading_hours_extended_start_nyse = datetime.time( 4, 0, 0, 0) # 4AM
    trading_hours_extended_end_nyse   = datetime.time(20, 0, 0, 0) # 8PM

    while True:
        # 1. Poll ALphaVantage for the quote of Gamestop.
        quote_data = await get_price_from_alphavantage_and_store(api_key, ticker)
        # Need error management when response negative!
        price = quote_data['Global Quote']['05. price']

        # 2. Write price for GME into DynamoDB.
        table_response = stockPriceTable.update_item(
            Key={
                'ticker': 'GME'
            },
            UpdateExpression="set price=:p",
            ExpressionAttributeValues={
                ':p': Decimal(price)
            },
            ReturnValues="UPDATED_NEW"
        )

        print(price)

        # 3. Sleep until it is time to poll again. Different intervals for trading hours and outside.
        now_datetime = datetime.datetime.utcnow()
        now_datetime_nyc = now_datetime - datetime.timedelta(seconds=timezone_delta_utc_to_eastern)

        # Check weekday AND time:
        if 1 <= now_datetime_nyc.isoweekday() <= 5 \
        and trading_hours_extended_start_nyse <= now_datetime_nyc.time() <= trading_hours_extended_end_nyse:
            current_polling_interval = polling_interval_trading_hours
        else:
            current_polling_interval = polling_interval_inactive_hours

        await asyncio.sleep(current_polling_interval)
        

async def main(stockPriceTable):
    await asyncio.gather( 
        update_timezone(), 
        quote_routine(stockPriceTable)
    )

if __name__ == '__main__':
    # Make sure that the prerequisites are there.
    # Global variables within script.
    price = 0
    timezone_delta_utc_to_eastern = 0

    # Get a connection to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    stockPriceTable = dynamodb.Table('stockPriceTable')
    
    # Run polling code.
    asyncio.run(main(stockPriceTable))