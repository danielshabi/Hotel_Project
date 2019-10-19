import psycopg2
from psycopg2.extras import Json
import yaml


class Db:
    def __init__(self):
        self.cfg = yaml.load(open(r'setting.yaml'), Loader=yaml.Loader)
        self.conn = None
        try:
            self.conn = psycopg2.connect(database=self.cfg["DB_NAME"], user=self.cfg["DB_USER"],
                                         password=self.cfg["DB_PASS"], host=self.cfg["DB_HOST"],
                                         port=self.cfg["DB_PORT"])
            print("Database Connected Successfully")
        except:
            print("Database Connection Failed")

    def get_reservation(self, res_id):
        result = {
            "DATA": {},
            "STATUS": "Fail"
        }
        if self.conn is None:
            result["ERROR"] = "Failed connecting to db"
            return result
        db = self.conn.cursor()
        query = "SELECT * FROM reservations where reservationid = {}".format(res_id)
        try:
            db.execute(query)
        except:
            result["ERROR"] = "Failed in query, please make sure the id parameter is OK"
            return result
        rows = db.fetchall()
        if len(rows) < 1:
            result["ERROR"] = f"There is no reservation with id: {res_id} ."
            return result
        rows = rows[0]
        db.close()
        result = {
            "DATA": {
                "ID": rows[0],
                "Hotel ID": rows[1],
                "Arrival Date": rows[2],
                "Departure Date": rows[3],
                "Status": rows[4],
                "Room Type": rows[5]
            },
            "STATUS": "Success"
        }
        return result

    def isexist(self, table, column, val):
        if self.conn is None:
            return False
        db = self.conn.cursor()
        query = "SELECT * FROM {} where {}= {}".format(table, column, val)
        try:
            db.execute(query)
        except:
            return False
        rows = db.fetchall()
        if len(rows) < 1:
            return False
        else:
            return True

    def create_reservation(self, hotel, arrive, depart, room):
        pass
