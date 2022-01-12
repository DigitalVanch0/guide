import os
import pathlib
import sqlite3
# import traceback
import random
import string
from datetime import date
import hashlib

import cherrypy


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


# класс описывающий таблицу пользователя
class User:
    def __init__(self, _id, fio: str, birthday: str, user_department: int, user_post: int, phone: str):
        self.id = _id
        self.fio = fio
        self.birthday = birthday
        self.user_department = user_department
        self.user_post = user_post
        self.phone = phone

    def __str__(self):
        return "User: id=%s, fio=%s, birthday=%s, user_department=%s, user_post=%s, phone=%s" % (
        self.id, self.fio, self.birthday,
        self.user_department, self.user_post,
        self.phone)


# класс описывающий таблицу должность
class Post:
    def __init__(self, _id: int, name: str, chief: str, admin: str):
        self.id = _id
        self.name = name
        self.chief = chief
        self.admin = admin

    def __str__(self):
        return "Post: id=%s, name=%s, chief=%s, admin=%s" % (self.id, self.name, self.chief, self.admin)


# класс описывающий таблицу файл
class File:
    def __init__(self, _id: int, file_name: str, format: str, time: str, size: int, data, user: int):
        self.id = _id
        self.file_name = file_name
        self.format = format
        self.time = time
        self.size = size
        self.data = data
        self.user = user

    def __str__(self):
        return "File: id=%s, name=%s, format=%s, time=%s, size=%s, data=%s, user=%s" % (self.id, self.file_name,
                                                                                        self.format,
                                                                                        self.time,
                                                                                        self.size, self.data,
                                                                                        self.user)


class Auth:
    def __init__(self, _id: int, login: str, password: str):

        self._id = _id
        self.login = login
        self.password = password

    def __str__(self):
        return "Auth: id=%s, login=%s, password=%s" % (self._id, self.login, self.password)



def readImage(filename):
    fin = open(filename, "rb")
    img = fin.read()
    format = pathlib.Path(filename).suffix
    size = os.path.getsize(filename)
    name = os.path.basename(filename)
    file_path = os.path.abspath(filename)
    fin.close()
    return [name, img, format, size // 1024, file_path]


class Spravochnik:
    def __init__(self):
        self.db = DBLayerORM("guide")

    def create(self, user: User):
        tmp = "INSERT INTO user (fio, birthday, user_department, user_post, phone) VALUES (?,?,?,?,?)"
        self.db.execute(tmp, (user.fio, user.birthday, user.user_department, user.user_post, user.phone))
        last_id = self.db.cursor.lastrowid
        user.id = last_id
        return user

    def update(self, user: User):
        tmp = "UPDATE user SET fio = ?, birthday = ?, user_department = ?, user_post = ?, phone = ? WHERE id = ?"
        self.db.execute(tmp, (user.fio, user.birthday, user.user_department, user.user_post, user.phone, user.id))

    def delete(self, user_id: int):
        tmp = "DELETE FROM user WHERE id =?"
        self.db.execute(tmp, (user_id,))

    def read_user(self, user_id: int):
        tmp = "SELECT * FROM user, file INNER JOIN file ON user.id = file.user"
        result = self.db.execute(tmp)
        if result.__len__() != 0:
            for i in result:
                id = i[0]
                if id == user_id:
                    return i
        else:
            return None

    def read_all_user(self):
        tmp = "SELECT user.id, user.fio, user.birthday, user.phone, post.post_name, department.department_name " \
              "FROM user, post, department WHERE user.user_post = post.id AND " \
              "user.user_department = department.id " \

        result = self.db.execute(tmp)
        if result.__len__() != 0:
            return result
        else:
            return None

    def read_post(self):
        tmp = "SELECT * FROM post"
        result = self.db.execute(tmp)
        if result.__len__() != 0:
            return result
        else:
            return None

    def fio_search(self, fio):
        tmp = "SELECT user.id, user.fio, user.birthday, user.phone, post.post_name, department.department_name FROM user, " \
              "post, department  WHERE user.user_post = post.id AND user.user_department = department.id"

        result = self.db.execute(tmp)
        res = []
        if result.__len__() != 0:
            for i in result:
                name = i[1]
                if fio in name:
                    res.append(i)
        else:
            return None
        return res

    def phone_search(self, phone):
        tmp = "SELECT user.id, user.fio, user.birthday, user.phone, post.post_name, department.department_name FROM user, " \
              "post, department  WHERE user.user_post = post.id AND user.user_department = department.id"
        result = self.db.execute(tmp)
        res = []
        if result.__len__() != 0:
            for i in result:
                number = i[3]
                if phone in number:
                    res.append(i)
        else:
            return None
        return res

    def get_all_files(self):
        tmp = "SELECT file.id, file.file_name, file.format, file.time, file.size, file.data, user.fio FROM file, " \
              "user WHERE file.file_user = user.id "
        result = self.db.execute(tmp)
        return result

    def upload_file(self, file: File):

        tmp = "INSERT INTO user (file_name, format, time, size, data, user) VALUES (?,?,?,?,?)"
        self.db.execute(tmp, (file.file_name, file.format, file.time, file.size, file.data, file.user))
        last_id = self.db.cursor.lastrowid
        file.id = last_id
        return file

    def searh_iso_type(self, form: str):
        tmp = "SELECT file.id, file.file_name, file.format, file.time, file.size, file.data, user.fio FROM file, " \
              "user WHERE file.file_user = user.id and format LIKE '%%%s%%'" % form
        result = self.db.execute(tmp)
        return result

    def search_iso_size(self, size):
        res_size = size
        tmp = "SELECT file.id, file.file_name, file.format, file.time, file.size, file.data, user.fio FROM file, " \
              "user WHERE file.file_user = user.id and size = '%%%s%%'" % res_size
        result = self.db.execute(tmp)
        return result

    def delete_file(self, file_name):
        tmp = "DELETE FROM file WHERE file_name =?"
        self.db.execute(tmp, (file_name,))

    def create_file(self, filedata, name):

        template = "SELECT COUNT (id) FROM file"
        count = self.db.execute(template)
        if count[0][0] < 20:
            tmp = "INSERT INTO file (file_name, format, time, size, data, file_user) VALUES (?,?,?,?,?,?)"
            res = readImage(filedata)
            time = date.today()
            self.db.execute(tmp, (res[0], res[2], time, res[3], res[4], name))
        else:
            return None


class AuthDao:
    def __init__(self):
        self.db = DBLayerORM("guide")

    def get(self, auth_id: int):
        tmp = "SELECT * FROM auth WHERE id=?"
        result = self.db.execute(tmp, (auth_id))
        return Auth(*result[0]) if result else []

    def get_all(self):
        tmp = "SELECT * FROM auth"
        res = self.db.execute(tmp)
        result = [Auth(*x) for x in res]
        return result

    def create(self, auth: Auth):
        try:
            check = self.get_all()
            if check[1] != auth.login:
                tmp = "INSERT INTO auth (login, password) VALUES(?,?)"
                hash = hashlib.sha512(auth.password.encode('utf-8')).hexdigest()
                self.db.execute(tmp, (auth.login, hash,))
                last_id = self.db.cursor.lastrowid
                auth.id = last_id
                return auth
            else:
                return "Пользователь уже существует"
        except:
            return None

    def find_by_session(self, session_id: str):
        tmp = "SELECT * FROM auth WHERE id=?"
        result = self.db.execute(tmp, (session_id))
        return Auth(*result[0]) if result else []

    def find_by_cred(self, login, password):
        tmp = "SELECT * FROM auth WHERE login=? AND password=?"
        hash = hashlib.sha512(password.encode('utf-8')).hexdigest()
        result = self.db.execute(tmp, (login, hash))
        if result != None:
            if result[0][1] == login and result[0][2] == hash:
                return 1
            else:
                return 0






def check_auth(target_func):
    def wrapper(self, *args):
        res = self.auth.find_by_session(1)
        if res:
            print('session: %s' % res)
            return target_func(*args)
        if not cherrypy.request.cookie.get('test_auth_key'):
            test_auth_key = 'test_key_' + str(random.randint(0, 100000))
            cherrypy.response.cookie['test_auth_key'] = test_auth_key
        else:
            test_auth_key = cherrypy.request.cookie.get('test_auth_key')
            return "error auth %s" % test_auth_key

    return wrapper


sprav = Spravochnik()
