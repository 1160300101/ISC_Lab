import pymysql
import threading
__metaclass__ = type


class DBHelper:
    @staticmethod
    def get_con(if_dict=True):
        config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '1026Lijing-=',
            'db': 'lsc_lab',
            'charset': 'utf8',
            'cursorclass': pymysql.cursors.DictCursor,
        }

        # config = {
        #     'host': 'localhost',
        #     'port': 3306,
        #     'user': 'root',
        #     'password': '1026Lijing-=',
        #     'db': 'lsc_lab',
        #     'charset': 'utf8',
        #     'cursorclass': pymysql.cursors.DictCursor,
        # }
        if not if_dict:
            config['cursorclass'] = pymysql.cursors.Cursor

        conn = pymysql.connect(**config)
        return conn

    @staticmethod
    def execute(sql,conn, args=None):

        if not conn:
            raise Exception("connect failed")
        try:
            cursor = conn.cursor()  # (pymysql.cursors.DictCursor)
            num = cursor.execute(sql, args)
        except :
           print("insert double")
           return 0,0
        return cursor, num

    @staticmethod
    def close(conn,cursor=None):
        if conn:
            conn.close()
        if cursor:
            cursor.close()

    def write_data(self,conn,proto,src_ip,dst_ip,sport,dport):
        cursor = None,
        try:
            sql = "insert into traffic_recognition_high_risk_traffic(proto,src_ip,dst_ip,sport,dport) values (%s, %s, %s, %s, %s)"
            cursor, num = self.execute(sql, args=(proto,src_ip,dst_ip,sport,dport), conn=conn)
            if cursor==0:
                return
        except :
            conn.rollback()
            print("insert double")

        finally:
            conn.commit()
            DBHelper.close(conn=conn,cursor=cursor)

    def write_bl(self, conn, ip):
        cursor = None,
        try:
            sql = "insert into traffic_recognition_black_list(ip) values (%s)"
            cursor, num = self.execute(sql, args=(ip), conn=conn)
        except Exception as e:
            conn.rollback()
            raise Exception("insert failed!")


        finally:
            conn.commit()
            DBHelper.close(conn=conn, cursor=cursor)

    def  delete_all(self,conn):
        cursor = None
        try:
            sql = "delete from traffic_recognition_high_risk_traffic"
            cursor, num = self.execute(sql, conn=conn)
        except Exception as e:
            conn.rollback()
            raise Exception("delete failed!")
        finally:
            conn.commit()
            DBHelper.close(conn, cursor=cursor)

    def delete_bl(self, conn):
        cursor = None
        try:
            sql = "delete from traffic_recognition_black_list"
            cursor, num = self.execute(sql, conn=conn)
        except Exception as e:
            conn.rollback()
            raise Exception("delete failed!")
        finally:
            conn.commit()

            DBHelper.close(conn, cursor=cursor)

    def read_data(self,id,conn):
        sql = "select * from  traffic_recognition_high_risk_traffic where id > " + str(id)
        cursor = None
        try:
            cursor, num = self.execute(sql, conn=conn)
            values = cursor.fetchall()
        except Exception as e:
            raise Exception("read failed!")
        finally:
            DBHelper.close(conn,cursor=cursor)
        return values

    def read_bl(self, id, conn):
        sql = "select id from traffic_recognition_black_list where id > " + str(id)
        cursor = None
        try:
            cursor, num = self.execute(sql, conn=conn)
            values = cursor.fetchall()
        except Exception as e:
            raise Exception("read failed!")
        finally:
            DBHelper.close(conn, cursor=cursor)
        return values

    def change_auto(self,conn):
        cursor = None
        try:
            sql = "alter table  traffic_recognition_high_risk_traffic auto_increment=1"
            cursor, num = self.execute(sql, conn=conn)
        except Exception as e:
            conn.rollback()
            raise Exception("change_auto failed")
        finally:
            conn.commit()
            DBHelper.close(conn, cursor=cursor)


    def change_auto_bl(self,conn):
        cursor = None
        try:
            sql = "alter table  traffic_recognition_black_list auto_increment=1"
            cursor, num = self.execute(sql, conn=conn)
        except Exception as e:
            conn.rollback()
            raise Exception("change_auto failed")
        finally:
            conn.commit()
            DBHelper.close(conn, cursor=cursor)

db = DBHelper()
conn_list = []


def theard_write(proto,src_ip,dst_ip,sport,dport):

   conn = DBHelper.get_con()
   t = threading.Thread(target=db.write_data,args=(conn,proto,src_ip,dst_ip,sport,dport,))
   t.start()
   return


def theard_write_bl(ip):

   conn = DBHelper.get_con()
   t = threading.Thread(target=db.write_bl,args=(conn,ip,))
   t.start()
   return


def read(id):
    conn = DBHelper.get_con()
    conn_list.append(conn)
    values = db.read_bl(id,conn)
    return values


def read_bl(id):
    conn = DBHelper.get_con()
    conn_list.append(conn)
    values = db.read_data(id, conn)
    return values

def delete():
    conn = DBHelper.get_con()
    conn_list.append(conn)
    db.delete_all(conn)
    db.delete_bl(conn)
    return

def set_auto():

    conn = DBHelper.get_con()
    conn_list.append(conn)
    db.change_auto(conn)
    db.change_auto_bl(conn)
    return

def db_close():
    for conn in conn_list:
        conn.close()
    return