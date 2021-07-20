from sqlalchemy import create_engine, MetaData, inspect, ForeignKeyConstraint, PrimaryKeyConstraint, select
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean
from  sqlalchemy_utils.functions import database


engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost", echo=False)

if not database.database_exists("mysql+pymysql://anonimo:Anonimo1%@localhost//University-project-BD/gym"):
    con = engine.connect()
    con.execute("commit")
    con.execute("create database if not exists gym ")
    #con.execute("set global activate_all_roles_on_login = on")  # attivazione di tutti i ruoli  (da decommentare dopo!)
    con.close()

engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")
metadata = MetaData()

utenti = Table('utenti',metadata,
           Column('id_utente',Integer,autoincrement=True),
           Column('nome',String(25)),
           Column('cognome',String(25)),
           Column('email',String(30)),
           Column('telefono',String(15)),
           Column('password',String(16),nullable=False),
           Column('Tampone',Boolean),
           PrimaryKeyConstraint('id_utente',name='utenti_pk')
           #Column('ruolo',enumerate((0,'gestore'),(1,'iStruttori'),('2','utenti')))
           )
#TODO: aggiungere colonne istruttore id e istruttre
corsi = Table('corsi',metadata,
          Column('id_corso', Integer,autoincrement=True),
          Column('nome', String(25)),
          PrimaryKeyConstraint('id_corso','nome',name='corsi_pk'),
          Column('descrizione', String(150))
          )

corsi_seguiti = Table('corsi_seguiti',metadata,
                Column('utente',None,ForeignKey('utenti.id_utente'),nullable=False),
                Column('corso_id',None,ForeignKey('corsi.id_corso'),nullable=False),
                )


#TODO :
locali = Table('locali',metadata,
               Column('id_locale', Integer, primary_key=True, autoincrement=True),
               Column('nome', String(25)),
               Column('mq', Float),
               Column('capienza', Integer)
              )
#TODO: aggiungere i collegamenti tra corso e id
lezioni = Table('lezioni',metadata,
                Column('id_lezione', Integer, primary_key=True, autoincrement=True),
                Column('descrizione', String(120)),
                Column('giorno',Date),
                Column('ora',DateTime)
                )


metadata.create_all(engine)
