import psycopg2
import yaml


class Db:
    """
    DB Class for managing app's db connections actions
    """
    def __init__(self):
        self.cfg = yaml.load(open(r'setting.yaml'), Loader=yaml.Loader)
        self.conn = None
        self.db = None
        self.error = {"STATUS": "FAILED"}
        self.success = {"STATUS": "SUCCESS"}
        if self.set_db_connection():
            self.close_db_connection()
            print("Database Connection Checked Successfully")
        else:
            raise ValueError("Database Connection Check Failed")

    def set_db_connection(self):
        """
        Setting all db connection variables(conn,db)
        :return: (bool) True if succeed | False if Failed
        """
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
        """
        Resetting all db connection variables(conn,db)
        """
        if self.db is not None:
            self.db.close()
        if self.conn is not None:
            self.conn.close()

    def exec_query(self, query):
        """
        Execute Query on DB
        :param query: (string) query to run
        :return: (bool) succeeded and got at least one row , (dict) client error response if False | (dict) query result
        """
        try:
            self.db.execute(query)
        except (Exception, psycopg2.Error) as e:
            print(f"Failed in query: {e}")
            self.close_db_connection()
            result = self.error.copy()
            result["ERROR"] = "Failed in query, make sure all parameters are ok"
            return False, result
        rows = self.db.fetchall()
        if len(rows) < 1:
            self.close_db_connection()
            result = self.error.copy()
            result["ERROR"] = "There is no rows that match the parameters provided"
            return False, result
        else:
            return True, rows

    def get_reservation(self, res_id):
        """
        Get reservation info by id
        :param res_id: (string) id of reservation
        :return: (dict) client response
        """
        if self.set_db_connection():

            query = "SELECT * FROM reservations where reservationid = {}".format(res_id)
            status, result = self.exec_query(query=query)
            if status is False:
                return result
            else:
                rows = result[0]
                result = {
                    "DATA": {
                        "ID": rows[0],
                        "Hotel ID": rows[1],
                        "Arrival Date": rows[2],
                        "Departure Date": rows[3],
                        "Status": rows[4],
                        "Room Type": rows[5]
                    },
                    "STATUS": "SUCCESS"
                }
                self.close_db_connection()
                return result
        else:
            result = self.error.copy()
            result["ERROR"] = f"There is an Error connecting to to the db, please try again later."
            return result

    def hotel_exist(self, hotel):
        """
        Check if hotel with specific id exists
        :param hotel: (int/string) hotel id
        :return: (bool) True/False
        """
        if self.set_db_connection():

            query = "SELECT * FROM hotels where hotelid= {}".format(hotel)
            status, result = self.exec_query(query=query)
            if status:
                self.close_db_connection()
            return status
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

    def get_room_count(self, hotel, room):
        """
        Get How many of specific room exists in hotel
        :param hotel: (string/int) hotel id
        :param room: (string) room name
        :return: False if not found or error | (int)_number of rooms if True
        """
        if self.set_db_connection():

            query = "SELECT (rooms->>{}) FROM hotels where hotelid= {} and (rooms->{}) IS NOT NULL"\
                .format(f"'{room.lower()}'", hotel, f"'{room.lower()}'")
            status, result = self.exec_query(query=query)
            if status:
                self.close_db_connection()
                return int(result[0][0])
            else:
                return False
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

    def room_avail(self, hotel, room, room_max, arrive, depart):
        """
        Check if room avail in time range
        :param hotel: (int/string) hotel id to search by
        :param room: (int/string) room to search
        :param room_max: (int) how many rooms like this exists
        :param arrive: (string) from date
        :param depart: (string) to date
        :return: (bool) True/False
        """
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
        """
        Create reservation
        :param hotel: (string) hotel to order in
        :param arrive: (string) arrival date
        :param depart: (string) departure date
        :param room: (string) room to order
        :return: (int) reservation id if Succeed | (bool) false if failed
        """
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
        """
        Cancell reservation
        :param res_id: (string) reservation id to cancel
        :return: (dict) client's response
        """
        success = self.success.copy()
        if self.set_db_connection():
            query = "SELECT * FROM reservations where reservationid = {}".format(res_id)
            status, result = self.exec_query(query=query)
            if status is False:
                return result
            else:
                if result[0][4] == "Cancelled":
                    result = self.error.copy()
                    result["ERROR"] = f"ID: {res_id} already cancelled"
                    self.close_db_connection()
                    return result
                query = "Update reservations set status = 'Cancelled' where reservationid={}".format(res_id)
                try:
                    self.db.execute(query)
                    self.conn.commit()
                    print("Reservation Cancelled Successfully")
                except (Exception, psycopg2.Error) as e:
                    print(f"Failed in create query: {e}")
                    self.close_db_connection()
                    result = self.error.copy()
                    result["ERROR"] = "Request Failed for unknown reason"
                    return result
                self.close_db_connection()
                return success
        else:
            print(f"There is an Error connecting to to the db, please try again later.")
            return False

    def inventory(self, hotel, date):
        """
        list inventory of hotel (how many occupied and available on each room on day supplied)
        :param hotel: (string/int) hotel id
        :param date: (string) date to check in
        :return: (dict) client's response
        """
        data = {}
        if self.set_db_connection():
            query = "SELECT rooms FROM hotels where hotelid={}".format(hotel)
            status, result = self.exec_query(query=query)
            if status is False:
                return False, result
            else:
                dic = result[0][0]
                for room in dic.keys():
                    data[room] = {"available": dic[room], "occupied": 0}
            query = "SELECT roomtype, COUNT(roomtype) FROM reservations WHERE hotelid={} " \
                    "AND arrivaldate<='{}' AND departuredate>='{}' AND status='Active' " \
                    "GROUP BY roomtype".format(hotel, date, date)
            status, result = self.exec_query(query=query)
            if status is False:
                if result["ERROR"] == "There is no rows that match the parameters provided":
                    return True, data
                else:
                    return False, result
            else:
                for room in result:
                    data[room[0]]['available'] -= room[1]
                    data[room[0]]['occupied'] += room[1]
        return True, data


