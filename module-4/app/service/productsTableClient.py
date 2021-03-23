import boto3
import json
import logging
from collections import defaultdict

client = boto3.client('dynamodb')

def getAllProducts():

    # Recupere todos los Productos de DynamoDB utilizando la operación scan de DynamoDB.
    # Nota: La API scan puede ser costosa en términos de latencia cuando un DynamoDB
    # contiene una gran cantidad de registros y se aplican filtros a la
    # operación que requiere que se escanee una gran cantidad de datos en la tabla
    # antes de que DynamoDB devuelva una respuesta. Para tablas de gran volumen que
    # reciben muchas solicitudes, es común almacenar el los resultados frecuentes / comunes
    # en una caché en memoria. Acelerador DynamoDB (DAX) o ElastiCache. 
    # Pero, como tenemos pocos productos, la API tiene poco tráfico y la tabla es muy pequeña, 
    #la operación de escaneo se adaptará a nuestras necesidades de momento.
    
    response = client.scan(
        TableName='ProductsTable'
    )

    logging.info(response["Items"])

    productsList = defaultdict(list)
    for item in response["Items"]:
        product = {}
        product["productId"] = item["ProductId"]["S"]
        product["name"] = item["Name"]["S"]
        product["prime"] = item["AmazonPrime"]["S"]
        product["descuento"] = item["DescuentoRegular"]["S"]
        product["type"] = item["Type"]["S"]
        product["thumbImageUri"] = item["ThumbImageUri"]["S"]
        productsList["products"].append(product)

    return json.dumps(productsList)

def queryProducts(queryParam):

    logging.info(json.dumps(queryParam))

    # Utilizamos la API Query de DynamoDB para recuperar los productos de la tabla que son
    # iguales a los filtros seleccionados
    response = client.query(
        TableName='ProductsTable',
        IndexName=queryParam['filter']+'Index',
        KeyConditions={
            queryParam['filter']: {
                'AttributeValueList': [
                    {
                        'S': queryParam['value']
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )

    productsList = defaultdict(list)
    for item in response["Items"]:
        product = {}
        product["productId"] = item["ProductId"]["S"]
        product["name"] = item["Name"]["S"]
        product["prime"] = item["AmazonPrime"]["S"]
        product["descuento"] = item["DescuentoRegular"]["S"]
        product["type"] = item["Type"]["S"]
        product["thumbImageUri"] = item["ThumbImageUri"]["S"]
        productsList["products"].append(product)

    return json.dumps(productsList)

# Recuperación de un solo producto desde DynamoDB utilizando su ProductId único
def getProduct(productId):

    response = client.get_item(
        TableName='ProductsTable',
        Key={
            'ProductId': {
                'S': productId
            }
        }
    )

    item = response["Item"]

    product = {}
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
    product["favorite"] = item["Favorite"]["BOOL"]

    return json.dumps(product)

# incrementar el número de Me gusta para un producto en 1
def likeProduct(productId):

    # Utilice el UpdateItem de la API de DynamoDB para incrementar el número de Me gusta
    # del producto en 1 usando una UpdateExpression.
    response = client.update_item(
        TableName='ProductsTable',
        Key={
            'ProductId': {
                'S': productId
            }
        },
        UpdateExpression="SET Likes = Likes + :n",
        ExpressionAttributeValues={':n': {'N': '1'}}
    )

    response = {}
    response["Update"] = "Success";

    return json.dumps(response)

# marcar un producto como favorito
def markFavorite(productId):

    # Utilice el UpdateItem de la API de DynamoDB para establecer el valor del producto favorito
    # a True usando una UpdateExpression.
    response = client.update_item(
        TableName='ProductsTable',
        Key={
            'ProductId': {
                'S': productId
            }
        },
        UpdateExpression="SET Favorite = :b",
        ExpressionAttributeValues={':b': {'BOOL': True}}
    )

    response = {}
    response["Update"] = "Success";

    return json.dumps(response)
