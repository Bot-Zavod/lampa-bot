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
            "conv_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	        "create_date"	date NOT NULL
            );
            """,
        ]

        for sql in sql_tables:
            self.cursor.execute(sql)
            self.conn.commit()

    # check iff the user has an active subscription
    def checkUserSubscribed(self, chat_id: int) -> bool:
        # compares the date today and subscribtion date
        sql = "SELECT EXISTS(SELECT * FROM Subscribers WHERE chat_id = (?) AND end_date >= DATE())"
        args = [chat_id]
        res = False
        try:
            self.cursor.execute(sql, args)
            cursor = self.cursor.fetchall()[0][0]
            # turn answer into boolean
            res = bool(cursor)
        except Exception as e:
            print(f"[ERROR] checkUserSubscribed\n{e}")
        finally:
            self.conn.commit()
            return res

    # Checks whether the user can make a free conversation
    def checkFreePass(self, chat_id: int) -> bool:
        res = True
        try:
            # checks if he had already used bot 3 times
            self.cursor.execute(
                "SELECT COUNT(*) FROM Passes WHERE chat_id = (?)", [chat_id]
            )
            data = self.cursor.fetchall()[0][0]
            print(data)
            if data < 3:
                res = True
            else:
                # if he had used it for 3 times checks if he had used it today
                self.cursor.execute(
                    "SELECT EXISTS(SELECT * FROM Passes WHERE chat_id = (?) AND create_date = DATE('now'))",
                    [chat_id],
                )
                data = self.cursor.fetchall()[0][0]
                res = not bool(data)
        except Exception as e:
            print(f"[ERROR] checkFreePass\n{e}\n")
        finally:
            self.conn.commit()
            return res

    # create a new pass with user chat_id
    def newPass(self, chat_id: int) -> None:
        sql = "INSERT INTO Passes (chat_id, create_date) VALUES (?, DATE())"
        args = [chat_id]
        try:
            self.cursor.execute(sql, args)
        except Exception as e:
            print(f"[ERROR] newPass\n{e}\n")
        finally:
            self.conn.commit()

        # create a new pass with user chat_id

    # get end date of user subscribtion
    def getEndDateSubscribed(self, chat_id: int) -> str:
        sql = "SELECT end_date FROM Subscribers WHERE chat_id = (?)"
        args = [chat_id]
        try:
            self.cursor.execute(sql, args)
            date = self.cursor.fetchall()[0][0]
        except Exception as e:
            print(f"[ERROR] getEndDateSubscribed\n{e}")
        finally:
            self.conn.commit()
            return date

    # create a new subscription
    def newSubscriber(self, chat_id: int, username: str, email: str, term: str) -> None:
        dates = {
            "3days":"+3 days",
            "week":"+7 days", 
            "month": "+1 month"
        }
        sql = "INSERT OR REPLACE INTO Subscribers VALUES (?, ?, ?, "
        # check if he subscribed now
        if self.checkUserSubscribed(chat_id):
            # if yes get the last date of his subscribtion
            date = self.getEndDateSubscribed(chat_id)
            # add new days to his last day
            sql += f"DATE('{date}','{dates[term]}'))"
        else:
            # if no use today as the dase
            sql += f"DATE('now','{dates[term]}'))"
        args = [chat_id, username, email]
        try:
            self.cursor.execute(sql, args)
        except Exception as e:
            print(f"[ERROR] newSubscriber\n{e}\n")
        finally:
            self.conn.commit()

    # create new payment data row
    def newPayment(self, payment_id: int, chat_id: int, term: str) -> None:
        sql = "INSERT INTO Payments (payment_id, chat_id, term, create_date)\
             VALUES (?, ?, ?, datetime('now'))"
        args = [payment_id, chat_id, term]
        try:
            self.cursor.execute(sql, args)
        except Exception as e:
            print(f"[ERROR] newPayment\n{e}\n")
        finally:
            self.conn.commit()

    # write a new conversation today
    def newConversation(self) -> None:
        sql = "INSERT INTO Conversations (create_date) VALUES (DATE('now'))"
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(f"[ERROR] newConversation\n{e}\n")
        finally:
            self.conn.commit()

    # return number of conversations
    def getConversationsCount(self) -> int:
        sql = "SELECT COUNT(*) FROM Conversations"
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()[0][0]
        except Exception as e:
            print(f"ERROR getConversationsCount\n{e}\n")
        finally:
            self.conn.commit()
            return data

    # return list of users chat_id who passed the test
    def getAllUsersID(self, table="Passes") -> list:
        # you can change table to get actual from Passes and Subscribers
        sql = f"SELECT DISTINCT chat_id FROM {table}"
        try:
            self.cursor.execute(sql)
            cursor = self.cursor.fetchall()
            users_ids = [chat_id[0] for chat_id in cursor]
        except Exception as e:
            print(f"ERROR getAllUsersID\n{e}\n")
        finally:
            self.conn.commit()
            return users_ids

    # count payments by subscription term
    def getCountByTerm(self, term: str) -> int:
        sql = f"SELECT COUNT(*) FROM Payments WHERE term='{term}'"
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()[0][0]      
        except Exception as e:
            print(f"ERROR getCountByTerm\n{e}\n")
        finally:
            self.conn.commit()
            return data

    # # returm list of all dates fields
    # def getDates(self):
    #     sql = "SELECT DATE(DATE) FROM Payments"
    #     try:
    #         self.cursor.execute(sql)
    #         data = self.cursor.fetchall()[0]            
    #     except sqlite3.IntegrityError:
    #         print("ERROR while checking the user")
    #     finally:
    #         self.conn.commit()
    #         print('FINALY')
    #         return data


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

    # for i in range(2,5):
    #     print(DB.checkUserSubscribed(i))

    print(DB.getCountByTerm("3days"))