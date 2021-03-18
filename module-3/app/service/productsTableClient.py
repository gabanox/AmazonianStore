import boto3
import json
import logging
from collections import defaultdict
import argparse

# create a DynamoDB client using boto3. The boto3 library will automatically
# use the credentials associated with our ECS task role to communicate with
# DynamoDB, so no credentials need to be stored/managed at all by our code!
client = boto3.client('dynamodb')

def getProductsJson(items):
    productsList = defaultdict(list)

    for item in items:
        mysfit = {}

        product["productId"] = item["ProductId"]["S"]
        product["name"] = item["Name"]["S"]
        product["type"] = item["Type"]["S"]
        product["description"] = item["Description"]["S"]
        product["price"] = int(item["Price"]["N"])
        product["prime"] = item["AmazonPrime"]["S"]
        product["descuento"] = item["DescuentoRegular"]["S"]
        product["thumbImageUri"] = item["ThumbImageUri"]["S"]
        product["profileImageUri"] = item["ProfileImageUri"]["S"]
        product["likes"] = item["Likes"]["N"]
        product["bought"] = item["Bought"]["BOOL"]

        productList["products"].append(product)

    return productsList

def getAllProducts():
    response = client.scan(
        TableName='ProductsTable'
    )

    logging.info(response["Items"])

    productsList = getProductsJson(response["Items"])

    return json.dumps(productsList)

def queryProductsItems(filter, value):
    response = client.query(
        TableName='ProductsTable',
        IndexName=filter+'Index',
        KeyConditions={
            filter: {
                'AttributeValueList': [
                    {
                        'S': value
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )

    productsList = getProductsJson(response["Items"])

    return json.dumps(productsList)

def queryProducts(queryParam):

    logging.info(json.dumps(queryParam))

    filter = queryParam['filter']
    value = queryParam['value']

    return queryProductsItems(filter, value)

# So we can test from the command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filter')
    parser.add_argument('-v', '--value')
    args = parser.parse_args()

    filter = args.filter
    value = args.value

    if args.filter and args.value:
        print(f'filter is {args.filter}')
        print(f'value is {args.value}')

        print('Getting filtered values')

        items = queryProductsItems(args.filter, args.value)
    else:
        print("Getting all values")
        items = getAllProducts()

    print(items)
