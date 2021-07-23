import sre_constants

from db import *

def delete_all(table):
    con.execute(table.delete())

def delete_user(email):
    query=text("select utenti.email from utenti where email = :x")
    con.execute(query, {"x": email})


def populate(x):
    if(x == False):
        global con
        con.close()
        query = text("Insert into utenti values (:a, :b,:c, :d, :e,:f,:g,:h)")
        con.execute(query, {"a": "0", "b": "Antonio", "c": "Rossi", "d": "antorossi@gmail.com", "e": "333321312",
                            "f": "mipalestra", "g": False, "h": "1"})
        query = text("Insert into utenti values (:a, :b,:c, :d, :e,:f,:g,:h)")
        con.execute(query,
                    {"a": "3", "b": "Luca", "c": "Bianchi", "d": "lucaross@gmail.com", "e": "3312321", "f": "cugiono12",
                     "g": False, "h": "2"})
        query = text("Insert into utenti values (:a, :b,:c, :d, :e,:f,:g,:h)")
        con.execute(query, {"a": "2", "b": "Lorenzo", "c": "rossi", "d": "lollorossi@gmail.com", "e": "4341121",
                            "f": "mypassione", "g": False, "h": "3"})
        con.close()
