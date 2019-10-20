import datetime


def get_reservation_validation(res_id, db):
    result = {"DATA": {}, "STATUS": "Fail"}

    # Check if user sent an id at all
    if not res_id:
        result["ERROR"] = "no id found, please send an id."
    # Check if the user entered a number not a name
    elif not str(res_id).isdigit():
        result["ERROR"] = "id must be numeric."

    # Now the user entered a valid id
    else:
        result = db.get_reservation(res_id)

    return result


def set_reservation_validation(json_data, db):
    result = {"STATUS": "Fail", "METHOD": "POST", "DATA": {}}
    success = {"STATUS": "Success", "METHOD": "POST"}

    if not all(x in json_data.keys() for x in ['hotel_id', 'arrival_date', 'departure_date', 'room_type']):
        result["ERROR"] = "Make sure all parameters delivered (hotel_id/arrival_date/departure_date/room_type)."
        return result

    hotel = json_data['hotel_id']
    arrive = json_data['arrival_date']
    depart = json_data['departure_date']
    room = json_data['room_type']

    if not type(hotel) is int:
        result["ERROR"] = "Hotel's id must be numeric."
        return result

    try:
        datetime.datetime.strptime(arrive, '%m/%d/%Y')
    except ValueError:
        result["ERROR"] = "Incorrect arrival date format, should be MM/DD/YYYY"
        return result

    try:
        datetime.datetime.strptime(depart, '%m/%d/%Y')
    except ValueError:
        result["ERROR"] = "Incorrect departure date format, should be MM/DD/YYYY"
        return result

    if type(room) is int:
        result["ERROR"] = "room type can't be numeric."
        return result

    if not db.hotel_exist(hotel):
        result["ERROR"] = f"The Hotel ID {hotel} is not exists."
        return result

    room_count = db.get_room_count(hotel, room)
    if room_count is None:
        result["ERROR"] = f"The room type {room} is not exists in hotel id: {hotel}."
        return result

    if not db.room_avail(hotel, room, room_count, arrive, depart):
        result["ERROR"] = f"All room type {room} in hotel id: {hotel} are full."
        return result

    res_id = db.create_reservation(hotel=hotel, arrive=arrive, depart=depart, room=room)

    if res_id is None:
        result["ERROR"] = "DB error processing request"
        return result

    success["DATA"] = {"ID": res_id}
    return success


def cancel_reservation_validation(res_id, db):
    result = {"STATUS": "Fail", "METHOD": "POST"}
    success = {"STATUS": "Success", "METHOD": "POST"}

    # Check if user sent an id at all
    if not res_id:
        result["ERROR"] = "no id found, please send an id."
    # Check if the user entered a number not a name
    elif not str(res_id).isdigit():
        result["ERROR"] = "id must be numeric."

    return db.cancel_reservation(res_id=res_id)
