import sys
import csv
import boto3

def main():
    num_args = len(sys.argv)

    if (num_args != 3):
        filename = input("Please enter a file name: ")
        tablename = input("Please enter a table name: ")

    else:
        filename = sys.argv[1]
        tablename = sys.argv[2]

    try:
        open(filename)
    except:
        print("Could not find file. Check to make sure it is in the same directory as this script.")

    attribute_definitions = [
        {
            'AttributeName': 'PartitionKey',
            'AttributeType': 'S',
        },
        {
            'AttributeName': 'Year',
            'AttributeType': 'N',
        },
    ]

    key_schema = [
        {
            'AttributeName': 'PartitionKey',
            'KeyType': 'HASH',
        },
        {
            'AttributeName': 'Year',
            'KeyType': 'RANGE',
        },
    ]

    client = boto3.client('dynamodb')

    try:
        response = client.create_table(AttributeDefinitions=attribute_definitions, KeySchema=key_schema, TableName=tablename, ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        })
    except client.exceptions.ResourceInUseException:
        print("Specified table name is already in use.")
        sys.exit()

    waiter = client.get_waiter('table_exists')

    waiter.wait(TableName=tablename, WaiterConfig={
        'Delay': 1
    })

    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            partition_key = row[0] + '-' + row[1]
            client.put_item(Item={
                'PartitionKey': {
                    'S': partition_key,
                },
                'Year': {
                    'N': row[2],
                },
                'Commodity': {
                    'S': row[0],
                },
                'Variable': {
                    'S': row[1]
                },
                'Units': {
                    'S': row[3]
                },
                'Mfactor': {
                    'N': row[4]
                },
                'Value': {
                    'N': row[5]
                },
            }, TableName=tablename)

main()