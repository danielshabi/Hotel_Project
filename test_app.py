from app import create_app
from db import Db
import json


def test_home():
    client = create_app().test_client()
    res = client.get('/')
    assert res.data == b'<h1>Server Is Running!</h1>', "Error in Index get response"


def test_set_cancel_get():
    client = create_app().test_client()
    data = {"hotel_id": 1, "arrival_date": '11/25/2019',
            "departure_date": '11/26/2019', "room_type": "deluxe room"}
    res = client.post(
        '/set_reservation',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert json.loads(res.data)["STATUS"] == "SUCCESS", "Error creating reservation"

    reservation_id = json.loads(res.data)["DATA"]["ID"]
    res = client.get(f'/get_reservation?id={reservation_id}')
    assert json.loads(res.data)["STATUS"] == 'SUCCESS',\
        f"Error in get reservation"

    res = client.post(f'/cancel_reservation?id={reservation_id}')
    assert json.loads(res.data)["STATUS"] == "SUCCESS", "Error cancelling reservation"


def test_clean_reservations():
    assert Db().clean_reservations(), "Reservation table cleanup error"


def test_list_room(hotel=1, arrive='11/25/2019', depart='11/26/2019'):
    client = create_app().test_client()
    res = client.get(f'/list_room?hotel_id={hotel}&arrival_date={arrive}&departure_date={depart}')
    assert json.loads(res.data)["STATUS"] == "SUCCESS", "Failed Getting the rooms inventory"
