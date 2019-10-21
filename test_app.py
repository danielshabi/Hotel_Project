from app import create_app
from db import Db
import json


def test_home(client):
    res = client.get('/')
    assert res.data == b'<h1>Server Is Running!</h1>', "Error in Index get response"


def test_get_reservation(client, reservation_id, result):
    res = client.get(f'/get_reservation?id={reservation_id}')
    assert json.loads(res.data)["STATUS"] == result,\
        f"Error in get reservation's {result} Status"


def test_clean_reservations():
    assert Db().clean_reservations(), "Reservation table cleanup error"


def test_set_reservation(client, data):
    res = client.post(
        '/set_reservation',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert json.loads(res.data)["STATUS"] == "SUCCESS", "Error creating reservation"
    return json.loads(res.data)["DATA"]["ID"]


def test_cancel_reservation(client, reservation_id):
    res = client.post(f'/cancel_reservation?id={reservation_id}')
    assert json.loads(res.data)["STATUS"] == "SUCCESS", "Error cancelling reservation"


def test_list_room(client, hotel, arrive, depart):
    res = client.get(f'/list_room?hotel_id={hotel}&arrival_date={arrive}&departure_date={depart}')
    assert json.loads(res.data)["STATUS"] == "SUCCESS", "Failed Getting the rooms inventory"


if __name__ == '__main__':
    cli = create_app().test_client()
    test_home(client=cli)
    test_get_reservation(client=cli, reservation_id=1, result='FAILED')
    res_id = test_set_reservation(client=cli, data={"hotel_id": 1, "arrival_date": '11/25/2019',
                                                    "departure_date": '11/26/2019', "room_type": "deluxe room"})
    test_get_reservation(client=cli, reservation_id=res_id, result='SUCCESS')
    test_cancel_reservation(client=cli, reservation_id=res_id)
    test_list_room(client=cli, hotel='1', arrive='11/25/2019', depart='11/26/2019')
    test_clean_reservations()
    print("Finished Successfully")
