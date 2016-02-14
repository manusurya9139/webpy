import web, datetime

db = web.database(dbn='postgres', db='protegrity', user='openuser', password="openpass")

def get_books():
    return db.select('books', order='id DESC')

def get_book(id):
    try:
        return db.select('books', where='id=$id', vars=locals())[0]
    except IndexError:
        return None

def add_book(name):
    db.insert('books', name=name, posted_on=datetime.datetime.utcnow())

def del_book(id):
    db.delete('books', where="id=$id", vars=locals())

def update_book(id, title, text):
    db.update('books', where="id=$id", vars=locals(),
        name=title)
