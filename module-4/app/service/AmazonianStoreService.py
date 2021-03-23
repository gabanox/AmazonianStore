from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import mysfitsTableClient

app = Flask(__name__)
CORS(app)

# The service basepath has a short response just to ensure that healthchecks
# sent to the service root will receive a healthy response.
@app.route("/")
def healthCheckResponse():
    return jsonify({"message" : "Nothing here, used for health check. Try /products instead."})

@app.route("/products", methods=['GET'])
def getProducts():

    filterCategory = request.args.get('filter')
    if filterCategory:
        filterValue = request.args.get('value')
        queryParam = {
            'filter': filterCategory,
            'value': filterValue
        }
        serviceResponse = productsTableClient.queryProducts(queryParam)
    else:
        serviceResponse = productsTableClient.getAllProducts()

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

@app.route("/products/<productId>", methods=['GET'])
def getProduct(productId):
    serviceResponse = productsTableClient.getProduct(productId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

@app.route("/products/<productId>/like", methods=['POST'])
def likeProduct(productId):
    serviceResponse = productsTableClient.likeProduct(productId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

@app.route("/products/<productId>/favorite", methods=['POST'])
def favoriteProduct(productId):
    serviceResponse = productsTableClient.markFavorite(productId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# Run the service on the local server it has been deployed to,
# listening on port 8080.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
