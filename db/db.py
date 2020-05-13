import sqlite3
from os import path, getcwd
from inspect import currentframe


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
            """
        ]

        for sql in sql_tables:
            self.cursor.execute(sql)
            self.conn.commit()

    # safely executes sql request
    def execute_sql(self, sql_and_args: list) -> None:
        try:
            self.cursor.execute(*sql_and_args)
        except Exception as e:
            function_name = currentframe().f_back.f_code.co_name
            print(f"[ERROR] {function_name}\n{e}\n")
        finally:
            self.conn.commit()

    # create a new pass with user chat_id
    def insertNewPass(self, chat_id: int) -> None:
        sql = "INSERT INTO Passes (chat_id, create_date) VALUES (?, DATE())"
        args = [chat_id]
        self.execute_sql([sql,args])



    ################################
    ############ CHECKS ############
    ################################

    # check if the user has an active subscription
    def userIsSubscribed(self, chat_id: int) -> bool:
        # compares the date today and subscribtion date
        sql = "SELECT EXISTS(SELECT * FROM Subscribers WHERE chat_id = (?) AND end_date >= DATE())"
        args = [chat_id]
        res = False
        self.execute_sql([sql,args])

        cursor = self.cursor.fetchall()[0][0]
        # turn answer into boolean
        answer = bool(cursor)
        return answer

    # Checks whether the user can make a free conversation
    def haveFreePass(self, chat_id: int) -> bool:
        res = True
        sql = "SELECT COUNT(*) FROM Passes WHERE chat_id = (?)"
        args = [chat_id]
        self.execute_sql([sql,args])
        data = self.cursor.fetchall()[0][0]

        if data < 3:
            res = True
        else:
            # if he had used it more than 3 times
            # checks if he had used it today
            sql = "SELECT EXISTS(SELECT * FROM Passes WHERE chat_id = (?) AND create_date = DATE('now'))"
            args = [chat_id]
            self.execute_sql([sql,args])
            data = self.cursor.fetchall()[0][0]
            res = not bool(data)
        return res

    # if it the first user time
    def firstTimeEntry(self, chat_id: int) -> bool:
        sql = "SELECT COUNT(*) FROM Passes WHERE chat_id = (?)"
        self.execute_sql([sql,[chat_id]])
        data = self.cursor.fetchall()[0][0]
        return not bool(data)



    ################################
    ############ PAYMENTS ##########
    ################################

    # get end date of user subscribtion
    def getEndDateSubscribed(self, chat_id: int) -> str:
        sql = "SELECT end_date FROM Subscribers WHERE chat_id = (?)"
        args = [chat_id]
        self.execute_sql([sql,args])
        date = self.cursor.fetchall()[0][0]
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
        if self.userIsSubscribed(chat_id):
            # if yes get the last date of his subscribtion
            date = self.getEndDateSubscribed(chat_id)
            # add new days to his last day
            sql += f"DATE('{date}','{dates[term]}'))"
        else:
            # if no use today as the dase
            sql += f"DATE('now','{dates[term]}'))"
        args = [chat_id, username, email]
        self.execute_sql([sql,args])

    # create new payment data row
    def createNewPayment(self, payment_id: int, chat_id: int, term: str) -> None:
        sql = "INSERT INTO Payments (payment_id, chat_id, term, create_date)\
             VALUES (?, ?, ?, datetime('now'))"
        args = [payment_id, chat_id, term]
        self.execute_sql([sql,args])



    ################################
    ######## ADMIN MODULE ##########
    ################################

    # return number of conversations
    def getConversationsCount(self) -> int:
        sql = "SELECT COUNT(*) FROM Conversations"
        self.execute_sql([sql])
        data = self.cursor.fetchall()[0][0]
        return data

    # return list of users chat_id who passed the test
    def getAllUsersID(self, table="Passes") -> list:
        # you can change table to get actual from Passes and Subscribers
        sql = f"SELECT DISTINCT chat_id FROM {table}"
        self.execute_sql([sql])
        
        cursor = self.cursor.fetchall()
        users_ids = [chat_id[0] for chat_id in cursor]
        return users_ids

    # count payments by subscription term
    def getCountByTerm(self, term: str) -> int:
        sql = f"SELECT COUNT(*) FROM Payments WHERE term='{term}'"
        self.execute_sql([sql])
        data = self.cursor.fetchall()[0][0]      
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
    # print(DB.firstTimeEntry(2))
    pass