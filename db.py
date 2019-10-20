import psycopg2
import yaml


class Db:
    def __init__(self):
        self.cfg = yaml.load(open(r'setting.yaml'), Loader=yaml.Loader)
        self.conn = None
        self.db = None
        if self.set_db_connection():
            self.close_db_connection()
            print("Database Connection Checked Successfully")
        else:
            raise ValueError("Database Connection Check Failed")

    def set_db_connection(self):
        try:
            self.conn = psycopg2.connect(database=self.cfg["DB_NAME"], user=self.cfg["DB_USER"],
                                         password=self.cfg["DB_PASS"], host=self.cfg["DB_HOST"],
                                         port=self.cfg["DB_PORT"])
            self.db = self.conn.cursor()
            return True
        except (Exception, psycopg2.Error) as e:
            print(f"Error connecting to DB: {e}")
            self.conn = None
            self.db = None
            return False

    def close_db_connection(self):
        if self.db is not None:
            self.db.close()
        if self.conn is not None:
            self.conn.close()

    def get_reservation(self, res_id):
        result = {
            "DATA": {},
            "STATUS": "Fail"
        }
        if self.set_db_connection():

            query = "SELECT * FROM reservations where reservationid = {}".format(res_id)
            try:
                self.db.execute(query)
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in get query: {e}")
                self.close_db_connection()
                result["ERROR"] = "Failed in query, please make sure the id parameter is OK"
                return result
            rows = self.db.fetchall()
            if len(rows) < 1:
                self.close_db_connection()
                result["ERROR"] = f"There is no reservation with id: {res_id} ."
                return result
            rows = rows[0]
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
            self.close_db_connection()
            return result
        else:
            result["ERROR"] = f"There is an Error connecting to to the db, please try again later."
            return result

    def exec_query(self, query, result=None):

        try:
            self.db.execute(query)
        except (Exception, psycopg2.Error) as e:
            print(f"Failed in query: {e}")
            self.close_db_connection()
            if result is None:
                return False
            else:
                result["ERROR"] = "Failed in query"
                return result
        rows = self.db.fetchall()
        if len(rows) < 1:
            self.close_db_connection()
            if result is None:
                return False
            else:
                result["ERROR"] = "There is no rows that match the values provided"
                return result
        else:
            self.close_db_connection()
            return rows

    def hotel_exist(self, hotel):
        if self.set_db_connection():

            query = "SELECT * FROM hotels where hotelid= {}".format(hotel)
            try:
                self.db.execute(query)
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in hotel query: {e}")
                self.close_db_connection()
                return False
            rows = self.db.fetchall()
            if len(rows) < 1:
                self.close_db_connection()
                return False
            else:
                self.close_db_connection()
                return True
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

    def get_room_count(self, hotel, room):
        if self.set_db_connection():

            query = "SELECT (rooms->>{}) FROM hotels where hotelid= {} and (rooms->{}) IS NOT NULL"\
                .format(f"'{room.lower()}'", hotel, f"'{room.lower()}'")
            try:
                self.db.execute(query)
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in room count query: {e}")
                self.close_db_connection()
                return None
            rows = self.db.fetchall()
            if len(rows) < 1:
                self.close_db_connection()
                return None
            else:
                self.close_db_connection()
                return int(rows[0][0])
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return None

    def room_avail(self, hotel, room, room_max, arrive, depart):
        if self.set_db_connection():

            query = "SELECT COUNT(roomtype) FROM reservations WHERE hotelid={} " \
                    "AND roomtype='{}' AND status='Active' AND" \
                    " ((arrivaldate <= '{}' AND departuredate >= '{}') OR" \
                    " (arrivaldate <= '{}' AND departuredate >= '{}')) GROUP BY roomtype" \
                .format(hotel, room.lower(), arrive, arrive, depart, depart)
            try:
                self.db.execute(query)
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in room avail query: {e}")
                self.close_db_connection()
                return False
            rows = self.db.fetchall()
            if len(rows) < 1:
                self.close_db_connection()
                return True
            else:
                self.close_db_connection()
                if room_max - (rows[0][0]+1) >= 0:
                    return True
                else:
                    return False
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

    def create_reservation(self, hotel, arrive, depart, room):
        if self.set_db_connection():
            query = "INSERT INTO reservations (hotelid, arrivaldate, departuredate, roomtype, status) " \
                    "VALUES ({}, '{}', '{}', '{}','Active') RETURNING reservationid".format(hotel, arrive, depart, room)
            try:
                self.db.execute(query)
                self.conn.commit()
                print("Table Created Successfully")
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in create query: {e}")
                self.close_db_connection()
                return False
            res_id = self.db.fetchone()[0]
            self.close_db_connection()
            return res_id
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

    def cancel_reservation(self, res_id):
        result = {"STATUS": "Fail", "METHOD": "POST"}
        success = {"STATUS": "Success", "METHOD": "POST"}
        if self.set_db_connection():
            query = "SELECT * FROM reservations where reservationid = {}".format(res_id)
            try:
                self.db.execute(query)
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in cancel query: {e}")
                self.close_db_connection()
                result["ERROR"] = "Failed in query"
                return result
            rows = self.db.fetchall()
            if len(rows) < 1:
                self.close_db_connection()
                result["ERROR"] = f"No ID: {res_id}"
                return result
            if rows[0][4] == "Cancelled":
                result["ERROR"] = f"ID: {res_id} already cancelled"
                return result
            query = "Update reservations set status = 'Cancelled' where reservationid={}".format(res_id)
            try:
                self.db.execute(query)
                self.conn.commit()
                print("Reservation Cancelled Successfully")
            except (Exception, psycopg2.Error) as e:
                print(f"Failed in create query: {e}")
                self.close_db_connection()
                result["ERROR"] = "Request Failed for unknown reason"
                return result
            self.close_db_connection()
            return success
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

