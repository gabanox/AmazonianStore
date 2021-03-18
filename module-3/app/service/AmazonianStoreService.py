from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import productsTableClient

# A very basic API created using Flask that has two possible routes for requests.

app = Flask(__name__)
CORS(app)

@app.route("/")
def healthCheckResponse():
    return jsonify({"message" : "Nothing here, used for health check. Try /products instead."})

@app.route("/products")
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

# Run the service on the local server it has been deployed to,
# listening on port 8080.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
