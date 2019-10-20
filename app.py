# app.py
from flask import Flask, request, jsonify
from db import Db
import utils

app = Flask(__name__)
db = Db()


@app.route('/get_reservation/', methods=['GET'])
def get_reservation():
    # Retrieve the id from url parameter
    res_id = request.args.get("id", None)
    # Run Validation Code
    result = utils.get_reservation_validation(res_id=res_id, db=db)
    # Return result as json
    return jsonify(result)


@app.route('/set_reservation/', methods=['POST'])
def set_reservation():
    # Retrieve the parameters as dict from user's json
    json_data = request.get_json()

    # Run Validation Code
    result = utils.set_reservation_validation(json_data=json_data, db=db)

    # Return result as json
    return jsonify(result)


@app.route('/cancel_reservation/', methods=['POST'])
def cancel_reservation():
    # Retrieve the id from url parameter
    res_id = request.args.get('id')

    # Run Validation Code
    result = utils.cancel_reservation_validation(res_id=res_id, db=db)

    # Return result as json
    return jsonify(result)

# Test our server State
@app.route('/')
def index():
    return "<h1>Server Is Running!</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
