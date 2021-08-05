import boto3
import sys
import csv

Variable = []
Commodity = []
Region = []
Unit = []
Mfactor = []

""" def get_value(array, idx, ) """

def query_table(table, key, client):
    response = client.query(
        TableName=table,
        ExpressionAttributeValues={
            ':v1': {
                'S': key
            }
        },
        KeyConditionExpression='PartitionKey = :v1'
    )

    if (response['Count'] != 0):
        return response['Items']
    else:
        return []

def read_encodings():
    try:
        open('encodings.csv')
    except:
        print("Could not find required encodings file.")
        sys.exit()

    with open('encodings.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (row[2] == 'commodity'):
                Commodity.append({
                    row[0]: row[1]
                })
            elif (row[2] == 'variable'):
                Variable.append({
                    row[0]: row[1]
                })
            elif (row[2] == 'unit'):
                Unit.append({
                    row[0]: row[1]
                })
            elif (row[2] == 'region'):
                Region.append({
                    row[0]: row[1]
                })
            elif (row[2] == 'mfactor'):
                Mfactor.append({
                    row[0]: row[1]
                })

def main():
    num_args = len(sys.argv)

    if (num_args != 2):
        commodity = input("Enter a commodity CODE: ")

    else:
        commodity = sys.argv[1]

    read_encodings()

    found = 0
    com_name = ''

    for i in Commodity:
        if (commodity in i):
            com_name = i[commodity]
            found = 1

    if (found == 0):
        print("Invalid commodity code")
        sys.exit()

    """ print(Variable) """

    client = boto3.client('dynamodb')

    """ Get all rows where commodity = input from na table"""

    """ check canada, if row key is  """

    """ response = client.query(
        TableName='northamericatest',
        ExpressionAttributeValues={
            ':v1': {
                'S': 'WT-IMaaaa'
            }
        },
        KeyConditionExpression='PartitionKey = :v1'
    ) """

    print("Commodity: ", com_name)

    total_can_usa = 0
    total_can_usa_mex = 0
    total_neither = 0

    for i in Variable:

        key, value = list(i.items())[0]
        to_search = commodity + '-' + key

        local_can_usa = 0
        local_can_usa_mex = 0
        local_neither = 0
        
        northamerica = query_table('northamerica', to_search, client)
        canada = query_table('canada', to_search, client)
        usa = query_table('usa', to_search, client)
        mexico = query_table('mexico', to_search, client)

        if (len(northamerica) == len(canada) == len(usa) == len(mexico) and len(northamerica) != 0):
            print("Variable: ", value)
            print('{:<6s} {:<15s} {:<12s} {:<12s} {:<12s} {:<12s} {:<12s} {:<15s}'.format('Year', 'North America', 'Canada', 'USA', 'Mexico', 'CAN+USA', 'CAN+USA+MEX', 'NA Defn'))

            for idx, item in enumerate(northamerica):
                na_defn = 'Neither'

                can_usa = float(canada[idx]['Value']['N']) + float(usa[idx]['Value']['N'])
                can_usa_mex = float(canada[idx]['Value']['N']) + float(usa[idx]['Value']['N']) + float(mexico[idx]['Value']['N'])

                na = float(northamerica[idx]['Value']['N'])

                can_usa = round(can_usa, 3)
                can_usa_mex = round(can_usa_mex, 3)
                na = round(na, 3)

                if (can_usa_mex == can_usa):
                    na_defn = 'Neither'
                    local_neither += 1
                elif (can_usa == na and na != 0):
                    na_defn = 'CAN+USA'
                    local_can_usa += 1
                elif (can_usa_mex == na):
                    na_defn = 'CAN+USA+MEX'
                    local_can_usa_mex += 1
                else:
                    na_defn = 'Neither'
                    local_neither += 1

                print('{:<6s} {:<15s} {:<12s} {:<12s} {:<12s} {:<12.3f} {:<12.3f} {:<10s}'.format(northamerica[idx]['Year']['N'], northamerica[idx]['Value']['N'], canada[idx]['Value']['N'], usa[idx]['Value']['N'], mexico[idx]['Value']['N'], can_usa, can_usa_mex, na_defn))

            print("North America Definition Results: ", str(local_can_usa) + '  CAN+USA,  ', str(local_can_usa_mex) + '  CAN+USA+MEX,  ', str(local_neither) + '  Neither')
            if (local_can_usa > local_can_usa_mex and local_can_usa > local_neither):
                print("Therefore we conclude North America = CAN+USA")
            elif(local_can_usa_mex > local_can_usa and local_can_usa_mex > local_neither):
                print("Therefore we conclude North America = CAN+USA+MEX")
            else:
                print("Therefore we conclude North America = Neither")
            
            print("")


            total_can_usa += local_can_usa
            total_can_usa_mex += local_can_usa_mex
            total_neither += local_neither
    
    print("Overall North America Definition Results: ", str(total_can_usa) + '  CAN+USA,  ', str(total_can_usa_mex) + '  CAN+USA+MEX,  ', str(total_neither) + '  Neither')
    if (total_can_usa > total_can_usa_mex and total_can_usa > total_neither):
        print("Conclusion for all" + com_name + "variables, North America = CAN+USA")
    elif(total_can_usa_mex > total_can_usa and total_can_usa_mex > total_neither):
        print("Conclusion for all" + com_name + "variables, North America = CAN+USA+MEX")
    else:
        print("Conclusion for all" + com_name + "variables, North America = Neither")

main()