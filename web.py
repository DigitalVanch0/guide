import cherrypy
import os
from jinja2 import *
from main import *
import rsa

conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.gzip.on': True,
        'tools.staticdir.root': os.path.abspath(os.getcwd()),
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './index.scss'

}
}

loader = FileSystemLoader('./')
env = Environment()
env.loader = loader
template = env.get_template('index.html')
template_guest = env.get_template('guest.html')

dict= {}

class UserService():
    def __init__(self):
        self.sprav = Spravochnik()
        self.auth = AuthDao()


    @cherrypy.expose
    def index(self):
         return template_guest.render()

    @cherrypy.expose
    def phone_search(self, phone):
     result = self.sprav.phone_search(phone)
     res = template.render({'result': result})
     return res



    @cherrypy.expose
    def login(self, login: str, passwd: str):
        authar = self.auth.find_by_cred(login, passwd)
        res = self.auth.find_by_cred(login, passwd)
        if res == 1:
            return template.render()
        else:
            return template_guest.render()

    @cherrypy.expose
    def registration(self, login, password):
        authar = Auth(None, login, password)
        res = self.auth.create(authar)
        return template.render()



    @cherrypy.expose
    def get_all_user(self):
        res = self.sprav.read_all_user()
        result = template.render({'result': res})
        return result

    @cherrypy.expose
    def fio_search(self, fio):
        result = self.sprav.fio_search(fio)
        res = template.render({'result': result})
        return res

    @cherrypy.expose
    def read_post(self):
        result = self.sprav.read_post()
        res = template.render({'res': result})
        return res


    @cherrypy.expose
    def update(self, id, fio, birth, user_department, user_post, phone):
        user = User(id, fio, birth, user_department, user_post, phone)
        res = self.sprav.update(user)
        return template.render()

    @cherrypy.expose
    def delete(self, user_id):
        res = self.sprav.delete(user_id)
        return template.render()


    @cherrypy.expose
    def create(self, fio, birth, department, post, phone):
        user = User(None, fio, birth, department, post, phone)
        res = self.sprav.create(user)
        return template.render()

    @cherrypy.expose
    def delete_file(self, file_name):
        self.sprav.delete_file(file_name)
        return template.render()

    @cherrypy.expose
    def update_file(self, file):
        pass


    @cherrypy.expose
    def add_file(self, file, user):
        self.sprav.create_file(file, user)


    @cherrypy.expose
    def file_search_type(self, file_type):
        r = self.sprav.searh_iso_type(file_type)
        result = template.render({'r': r})
        return result

    @cherrypy.expose
    def file_search_size(self, file_size):
        r = self.sprav.searh_iso_type(file_size)
        result = template.render({'r': r})
        return result


    @cherrypy.expose
    def read_all_files(self):
        r = self.sprav.get_all_files()
        result = template.render({'r': r})
        return result



root = UserService()
cherrypy.quickstart(root, "/", conf)


