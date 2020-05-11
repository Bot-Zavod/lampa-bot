import sqlite3
from os import path, getcwd

# Для Димы проверка FIRST TIME? -> checkFreePass()


class DBInterface:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.admins = []  # Сюда просто пихаем админов и все

        sql_tables = [
            # Payments table
            """
            CREATE TABLE IF NOT EXISTS `Payments` (
            `payment_id` integer PRIMARY KEY NOT NULL,
            `chat_id` integer NOT NULL,
            `term` varchar(255) NOT NULL,
            `create_date` datetime NOT NULL
            )
            """,
            # Subscribers table
            """
            CREATE TABLE IF NOT EXISTS `Subscribers` (
            `chat_id` integer PRIMARY KEY NOT NULL,
            `username` varchar(255) NOT NULL,
            `email` varchar(255) NOT NULL,
            `end_date` date NOT NULL
            )
            """,
            # Passes table
            """
            CREATE TABLE IF NOT EXISTS `Passes` (
            `pass_id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            `chat_id` integer NOT NULL,
            `create_date` date NOT NULL
            )
            """,
            # Conversations table
            """
            CREATE TABLE IF NOT EXISTS `Conversations` (
            `conv_id` integer PRIMARY KEY NOT NULL,
            `create_date` date NOT NULL
            );
            """,
        ]

        for sql in sql_tables:
            self.cursor.execute(sql)
            self.conn.commit()

    def checkUserApply(self, chat_id):
        """ Checks whether the user can co-talk """
        sql = "SELECT EXISTS(SELECT * FROM Subscribers WHERE chat_id = (?) and end_date >= DATE())"
        args = [chat_id]
        res = False
        try:
            self.cursor.execute(sql, args)
            cursor = self.cursor.fetchall()[0][0]
            res = True if cursor == 1 else False
        except sqlite3.IntegrityError:
            print("ERROR while checking the user")
        finally:
            self.conn.commit()
            print("FINALY")
            return res

    def checkFreePass(self, chat_id):
        """Checks whether the user can make a free conversation"""
        """ 1. Чтоб True у юзера должно быть меньше 3х или меньше 1го в день"""
        res = None
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM Passes WHERE chat_id = (?)", [chat_id]
            )
            data = self.cursor.fetchall()[0][0]
            if data <= 3:
                res = True
            else:
                self.cursor.execute(
                    "SELECT EXISTS(SELECT * FROM Passes WHERE chat_id = (?) AND create_date = DATE()",
                    [chat_id],
                )
                data = self.cursor.fetchall()[0][0]
                res = False if data == 1 else True
        except:
            print(f"Your request get_payment_id {chat_id} failed")
        finally:
            self.conn.commit()
        return res

    def newPass(self, chat_id):
        """create a new pass"""
        sql = "INSERT INTO Passes (chat_id, create_date) VALUES (?, DATE())"
        args = [chat_id]
        data = False
        try:
            self.cursor.execute(sql, args)
            data = True
        except:
            print(f"Your request {chat_id} failed;")
        finally:
            self.conn.commit()
        return False

    def newSubscriber(self, chat_id, username, email):
        sql = "INSERT INTO Subscribers VALUES (?, ?, ?, DATE())"
        args = [chat_id, username, email]
        data = False
        try:
            self.cursor.execute(sql, args)
            data = True
        except:
            print(f"Your request newSubscribe {chat_id} failed")
        finally:
            self.conn.commit()
        return data

    def updateSubscribeDate(self, chat_id, term):
        sql = (
            "UPDATE Subscribers SET end_date = DATE(end_date,(?)) WHERE chat_id = (?) ;"
        )
        args = [term, chat_id]

    def newPayment(self, chat_id, term):
        sql = "INSERT INTO Payments (chat_id, term, create_date)VALUES (?, ?, datetime('now'))"
        args = [chat_id, term]
        data = False
        try:
            self.cursor.execute(sql, args)
            data = True
        except:
            print(f"Your request newPayment has failed")
        finally:
            self.conn.commit()
        return data

    def newConversation(self):
        # conv_id must be Auto Increment
        sql = "INSERT INTO Conversations VALUES (DATE())"
        try:
            self.cursor.execute(sql)
            cursor = self.cursor.fetchall()
        except sqlite3.IntegrityError:
            print("ERROR while checking the user")
        finally:
            self.conn.commit()
            print("FINALY")

    def getConversationsCount(self):
        sql = "SELECT COUNT(*) FROM Conversations"
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()[0][0]
        except Exception as e:
            print(f"ERROR getConversationsCount\n{e}")
        finally:
            self.conn.commit()
            return data

    def getAllUsersID(self, table="Passes"):
        """Must return list of chat_id"""
        """U can change table to get actual from Passes and Subscribers"""
        sql = "SELECT DISTINCT chat_id FROM Passes"
        args = [table]
        try:
            self.cursor.execute(sql)
            cursor = self.cursor.fetchall()
        except Exception as e:
            print(f"ERROR getAllUsersID\n{e}")
        finally:
            self.conn.commit()
            return list(cursor)

    def getCountByTerm(self, term):
        # must return INT number ( count of records )
        sql = f"SELECT COUNT(*) FROM Payments WHERE term=\"{term}\""
        # args = [term]
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()[0][0]      
        except Exception as e:
            print(f"ERROR getCountByTerm\n{e}")
        finally:
            self.conn.commit()
            return data


    def getDates(self):
        # Must returm list of all dates fields
        sql = "SELECT DATE(DATE) FROM Payments;"
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()[0]            
        except sqlite3.IntegrityError:
            print("ERROR while checking the user")
        finally:
            self.conn.commit()
            print('FINALY')
            return data


# setting up the database
def start_database():
    database = "database.db"
    # if no db file -> create one
    if not path.exists(database):
        print("no database found")
        create_path = path.abspath(getcwd())
        create_path = path.join(create_path, database)
        print(f"create_path: {create_path}")
        f = open(create_path, "x")
        f.close()
    else:
        print("Database exist")
    full_path = path.abspath(path.expanduser(path.expandvars(database)))
    DB = DBInterface(full_path)
    return DB
DB = start_database()


if __name__ == "__main__":
    # print(DB.checkUserApply(1))
    # print(DB.newPayment(12242342342,30))
    print(DB.checkFreePass(100500),DB.checkUserApply(100500))
    DB.newPass(100500)
    print(DB.checkFreePass(100500),DB.checkUserApply(100500))