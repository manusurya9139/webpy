import web
import model
import os

urls = (
    '/', 'Index',
    '/login', 'Login',
    '/logout', 'Logout',
    '/performance','Performance',
    '/bookslibrary','BooksLibrary',
    '/list', 'List',
    '/books/add', 'Add',
    '/books/delete', 'Delete',
    '/books/(.*)','Books'
)

""" DB """
db = web.database(dbn='postgres', user='openuser', pw='openpass', db='protegrity')

""" GLOBALS """
myglobals = {
   'books' : list(db.query("SELECT * FROM books ORDER BY name")),
   'menu' : [
        ("/performance", "PERFORMANCE"),
        ("/bookslibrary", "BOOKS LIBRARY"),
        ("/logout", "LOGOUT"),
    ]
}

""" RENDER """
render = web.template.render('templates/', base='base', globals=myglobals)
render_plain = web.template.render('templates/')

""" SESSIONS """
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

allowed = (
    ('user','pass'),
)

class Login:

    login_form = web.form.Form( web.form.Textbox('Username', web.form.notnull),
        web.form.Password('Password', web.form.notnull),
        web.form.Button('Login'),
        )

    def GET(self):
        f = self.login_form()
        return render_plain.login(f)

    def POST(self):
        if not self.login_form.validates():
            return render_plain.login(self.login_form)

        username = self.login_form['Username'].value
        password = self.login_form['Password'].value
        
        if (username,password) in allowed:
            session.logged_in = True
            raise web.seeother('/')

        return render_plain.login(self.login_form)


class Logout:
    def GET(self):
        session.logged_in = False
        raise web.seeother('/login')


class Index:

    def GET(self):
        if session.get('logged_in', False):
            """ Show Performance """
            data = {}
            data['cpu'] = str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())
            data['mem'] = str(os.popen("top -n1 | awk '{sum=sum+$6}; END {print sum/1024}'").readline().strip())
            return render.performance(data)
        else:
            raise web.seeother('/login')
    

class Performance:

    def GET(self):
        if session.get('logged_in', False):
            """ Show Performance """
            data = {}
            data['cpu'] = str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())
            data['mem'] = str(os.popen("top -n1 | awk '{sum=sum+$6}; END {print sum/1024}'").readline().strip())
            return render.performance(data)
        else:
            raise web.seeother('/login')

class BooksLibrary:
    
    def GET(self):
        if session.get('logged_in', False):
            return render.bookslibrary()
        else:
            raise web.seeother('/login')
        

class List:

    def GET(self):
        books = model.get_books()
        return render.index(books)

class Add:
    
    form_addbook = web.form.Form(
        web.form.Textbox('name', web.form.notnull, size=30, description="Book name:"),
        web.form.Button('Add book'),
    )

    def GET(self):
        form = self.form_addbook()
        return render.add(form.render())

    def POST(self):
        form = self.form_addbook()
        if not form.validates():
            return render.add(form.render())
        model.add_book(form.d.name)
        raise web.seeother('/books/list')


class Delete:

    form_delete_book = web.form.Form(
        web.form.Textbox('name', web.form.notnull, size=30, description="Book name:"),
        web.form.Button('Delete book'),
    )

    def GET(self):
        form = self.form_delete_book()
        return render.delete('id', form.render())

    def POST(self):
        form = self.form_delete_book()
        if not form.validates():
            return render.delete('id',form.render())
        book = form['name'].value
        
        books = db.select("books")
        book_id = [ b.id for b in books if book == b.name]
        model.del_book(int(book_id[0]))
        raise web.seeother('/books/list')

class Books:

    def GET(self, link):
        if session.get('logged_in', False):
            
            books = model.get_books()
            if link == "list":
                return render.list(books)
            elif link == "add":
                return render.add(Add.form_addbook())
            elif link == "delete":
                return render.add(Delete.form_delete_book())
            raise web.seeother('/')
        else:
            raise web.seeother('/login')


app = web.application(urls, globals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session


if __name__ == '__main__':
    web.httpserver.runsimple(app.wsgifunc(), ("127.0.0.1", 8000))
