from db import *

def delete_all(table):
    con.execute(table.delete())


