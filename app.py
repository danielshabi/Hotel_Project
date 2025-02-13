# app.py
from flask import Flask, request, jsonify
from db import Db
import utils

db = Db()


def create_app():
    """Create and configure an instance of the Flask application."""

    app = Flask(__name__)

    def get_reservation():
        # Retrieve the id from url parameter
        res_id = request.args.get("id", None)
        # Run Validation Code
        result = utils.get_reservation_validation(res_id=res_id, db=db)
        # Return result as json
        return jsonify(result)

    def set_reservation():
        # Retrieve the parameters as dict from user's json
        json_data = request.get_json()

        # Run Validation Code
        result = utils.set_reservation_validation(json_data=json_data, db=db)

        # Return result as json
        return jsonify(result)

    def cancel_reservation():
        # Retrieve the id from url parameter
        res_id = request.args.get('id')

        # Run Validation Code
        result = utils.cancel_reservation_validation(res_id=res_id, db=db)

        # Return result as json
        return jsonify(result)

    def list_room():
        # Retrieve the id from url parameter
        hotel = request.args.get('hotel_id')
        arrive = request.args.get('arrival_date')
        depart = request.args.get('departure_date')

        # Run Validation Code
        result = utils.list_room_validation(hotel=hotel, arrive=arrive, depart=depart, db=db)

        # Return result as json
        return jsonify(result)

    def index():
        return "<h1>Server Is Running!</h1>"

    app.add_url_rule("/get_reservation", endpoint="get_reservation",
                     view_func=get_reservation, methods=['GET'])
    app.add_url_rule("/set_reservation", endpoint="set_reservation",
                     view_func=set_reservation, methods=['POST'])
    app.add_url_rule("/cancel_reservation", endpoint="cancel_reservation",
                     view_func=cancel_reservation, methods=['POST'])
    app.add_url_rule("/list_room", endpoint="list_room",
                     view_func=list_room, methods=['GET'])
    app.add_url_rule("/", endpoint="index",
                     view_func=index, methods=['GET'])

    return app


application = create_app()

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    application.run(threaded=True, port=5000)
