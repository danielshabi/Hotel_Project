# app.py
from flask import Flask, request, jsonify
from db import Db

app = Flask(__name__)
db = Db()


@app.route('/get_reservation/', methods=['GET'])
def get_reservation():
    # Retrieve the name from url parameter
    res_id = request.args.get("id", None)
    result = {"DATA": {}, "STATUS": "Fail"}
    # For debugging
    print(f"got id {res_id}")

    # Check if user sent an id at all
    if not res_id:
        result["ERROR"] = "no id found, please send an id."
    # Check if the user entered a number not a name
    elif not str(res_id).isdigit():
        result["ERROR"] = "id must be numeric."

    # Now the user entered a valid id
    else:
        result = db.get_reservation(res_id)

    # Return result as json
    return jsonify(result)


@app.route('/set_reservation/', methods=['POST'])
def post_something():
    json_data = request.get_json()
    hotel = json_data['hotel_id']
    arrive = json_data['arrival_date']
    depart = json_data['departure_date']
    room = json_data['room_type']

    result = {"STATUS": "Fail", "METHOD": "POST"}

    #print(f"Got:\n hotel: {hotel}\n arrival: {arrive}\n departure: {depart}\n room: {room}")

    #if not (hotel & arrive & depart & room):
    #    result["ERROR"] = "Make sure all parameters delivered (hotel_id/arrival_date/departure_date/room_type)."
    #    return result
    if db.isexist('hotels', 'hotelid', '{}'.format(hotel)):
       pass
    return jsonify(result)

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
