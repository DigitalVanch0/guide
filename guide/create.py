import sqlite3
import os
class DBLayerORM:
    def __init__(self, path: str):
        super().__init__()
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.path = path

    def __crete_connect(self):
        if os.path.exists(self.path):
            self.conn = sqlite3.connect(self.path, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
            self.conn.execute('pragma foreign_keys=ON')
        else:
            raise IOError("db not found")

    def create_cursor(self):
        self.__crete_connect()
        if self.conn:
            self.cursor = self.conn.cursor()
            print("create cursor")

    def close(self):
        if self.cursor:
            self.cursor.close()
            print("cursor close")
        if self.conn:
            self.conn.close()
            print("conn close")

    def execute(self, sql: str, attr=()):
        self.create_cursor()
        if self.cursor:
            self.cursor.execute(sql, attr)
            self.conn.commit()
            return self.cursor.fetchall()



db_layer = DBLayerORM('guide')
db_layer.execute("""CREATE TABLE auth(
                id INTEGER PRIMARY KEY,
                login TEXT,
                password VARCHAR(280))
                """)

db_layer.execute("""CREATE TABLE post(
    id INTEGER PRIMARY KEY,
    post_name TEXT NOT NULL,
    chief  TEXT NOT NULL,
    administrator TEXT NOT NULL)
    """)

db_layer.execute("""CREATE TABLE department(
    id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL,
    chief TEXT NOT NULL)
    """)

db_layer.execute("""CREATE TABLE user(
    id INTEGER PRIMARY KEY,
    fio TEXT NOT NULL,
    birthday TEXT NOT NULL,
    user_department INTEGER,
    user_post INTEGER NOT NULL,
    phone TEXT NOT NULL,
    FOREIGN KEY(user_department) REFERENCES department(id),
    FOREIGN KEY(user_post) REFERENCES post(id)
    )
    """)

db_layer.execute("""CREATE TABLE file(
    id  INTEGER PRIMARY KEY,
    file_name TEXT,
    format TEXT,
    time TEXT,
    size INTEGER,
    data TEXT,
    file_user INTEGER,
    FOREIGN KEY(file_user) REFERENCES user(id)
)   
""")







tmp_user = "INSERT INTO user(fio, birthday, user_department, user_post, phone) VALUES (?,?,?,?,?)"
tmp_post = "INSERT INTO post(post_name, chief, administrator) VALUES (?,?,?)"
tmp_department = "INSERT INTO department(department_name, chief) VALUES (?,?)"




db_layer.execute(tmp_post, ("accountant", "sachkov", "petr petrov"))
db_layer.execute(tmp_post, ("programmer", "magamedov", "petr petrov"))
db_layer.execute(tmp_post, ("web-designer", "magamedov", "petr petrov"))
db_layer.execute(tmp_post, ("clean-master", "sadykov", "petr petrov"))

db_layer.execute(tmp_department, ("accounting", "sachkov"))
db_layer.execute(tmp_department, ("it", "magamedov"))
db_layer.execute(tmp_department, ("cleening", "sadykov"))

db_layer.execute(tmp_user, ("tolya perov alexeevich", "27.10.2000", 1, 1, '89162349654'))
db_layer.execute(tmp_user, ("alex pehov pavlovich", "13.04.2000", 2, 2, '89773664406'))
db_layer.execute(tmp_user, ("darya ustina alexeevna", "14.05.2000", 2, 3, '89643567890'))
db_layer.execute(tmp_user, ("alexey prymougolniy anatolyevich", "29.03.1988", 3, 4, '89251234567'))
db_layer.execute(tmp_user, ("ivan semin denisovich", "29.04.2001", 3, 4, '89647225039'))

#tmp_user = "INSERT INTO user(fio, birthday, department, post, phone) VALUES (?,?,?,?,?)"
#tmp_post = "INSERT INTO post(name, chief, administrator) VALUES (?,?,?)"
#tmp_department = "INSERT INTO department(name, chief) VALUES (?,?)"


