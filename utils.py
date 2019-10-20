import datetime


def check_date(arrive, depart):
    """
    Check if arrival date and departure date are valid dates.
    Check if arrival date is before departure date.
    Check both dates are in future
    :param arrive: (string) arrival date
    :param depart:(string) departure date
    :return: (bool) False/True, (string) error if there is one
    """
    try:
        datetime.datetime.strptime(arrive, '%m/%d/%Y')
    except ValueError:
        err = "Incorrect arrival date format, should be MM/DD/YYYY"
        return False, err

    try:
        datetime.datetime.strptime(depart, '%m/%d/%Y')
    except ValueError:
        err = "Incorrect departure date format, should be MM/DD/YYYY"
        return False, err

    if (datetime.datetime.strptime(arrive, '%m/%d/%Y').date() >= datetime.datetime.strptime(depart, '%m/%d/%Y').date())\
        or (datetime.datetime.strptime(arrive, '%m/%d/%Y').date() <= datetime.datetime.today().date()) \
            or (datetime.datetime.strptime(depart, '%m/%d/%Y').date() <= datetime.datetime.today().date()):
        err = "Error: please make sure the arrival date is at least one day before departure and that the" \
                          " reservation is in the future and not today or in the past"
        return False, err
    return True, ""


def get_reservation_validation(res_id, db):
    """
    Function to validate the "get_reservation" app's endpoint and return client response
    :param res_id: (string) client's supplied reservation id
    :param db: (DB Class) db connection
    :return: (dict) client response
    """
    result = {"DATA": {}, "STATUS": "FAILED"}

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
    """
    Function to validate the "set_reservation" app's endpoint and return client response
    :param json_data: (dict) client's supplied json
    :param db: (DB Class) db connection
    :return: (dict) client response
    """
    result = {"STATUS": "FAILED", "DATA": {}}
    success = {"STATUS": "SUCCESS"}

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

    status, err = check_date(arrive=arrive, depart=depart)
    if status is False:
        result["ERROR"] = err
        return result

    if type(room) is int:
        result["ERROR"] = "room type can't be numeric."
        return result

    if not db.hotel_exist(hotel):
        result["ERROR"] = f"The Hotel ID {hotel} is not exists."
        return result

    room_count = db.get_room_count(hotel, room)
    if room_count is False:
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
    """
    Function to validate the "cancel_reservation" app's endpoint and return client response
    :param res_id: (string) client's supplied reservation id
    :param db: (DB Class) db connection
    :return: (dict) client response
    """
    result = {"STATUS": "FAILED"}
    success = {"STATUS": "SUCCESS"}

    # Check if user sent an id at all
    if not res_id:
        result["ERROR"] = "no id found, please send an id."
    # Check if the user entered a number not a name
    elif not str(res_id).isdigit():
        result["ERROR"] = "id must be numeric."

    return db.cancel_reservation(res_id=res_id)


def list_room_validation(hotel, arrive, depart, db):
    """
    Function to validate the "list_room" app's endpoint and return client response
    :param hotel: (string) client's supplied hotel id
    :param arrive: (string) client's supplied arrival date
    :param depart: (string) client's supplied departure date
    :param db: (DB Class) db connection
    :return: (dict) client response
    """
    result = {"DATA": {}, "STATUS": "FAILED"}
    success = {"STATUS": "SUCCESS"}

    # Check if user sent all params at all
    if not hotel or not arrive or not depart:
        result["ERROR"] = "missing parameters, make sure you provided: hotel_id/arrival_date/departure_date"

    # Check if the user entered a number not a name
    if not str(hotel).isdigit():
        result["ERROR"] = "id must be numeric."

    status, err = check_date(arrive=arrive, depart=depart)
    if status is False:
        result["ERROR"] = err
        return result
    arrive_date = datetime.datetime.strptime(arrive, '%m/%d/%Y')
    depart_date = datetime.datetime.strptime(depart, '%m/%d/%Y')
    data = {}
    while arrive_date <= depart_date:
        res, inventory = db.inventory(hotel=hotel, date=arrive)
        if res is False:
            return inventory
        else:
            data[arrive] = inventory
            arrive_date = arrive_date + datetime.timedelta(days=1)
            arrive = arrive_date.strftime('%m/%d/%Y')
    success["DATA"] = data
    return success
