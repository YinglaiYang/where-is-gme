startLocalDynamodb:
	@java -Djava.library.path=./local_mocks/dynamodb_local/DynamoDBLocal_lib -jar ./local_mocks/dynamodb_local/DynamoDBLocal.jar -sharedDb

runPollingLocally:
	@python3 ./data_polling/quotepoller.py

serveLocally: startLocalDynamodb runPollingLocally
