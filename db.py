import enum

from sqlalchemy import create_engine, MetaData, inspect, ForeignKeyConstraint, PrimaryKeyConstraint, select
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean,Enum,text
from  sqlalchemy_utils.functions import database

class Ruoli(enum.Enum):
    Gestore=1
    Istruttore=2
    Cliente=3
    Anonimo=4




engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost", echo=False)

if not database.database_exists("mysql+pymysql://anonimo:Anonimo1%@localhost//University-project-BD/gym"):
    con = engine.connect()
    con.execute("commit")
    con.execute("create database if not exists gym ")

    engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")
    metadata = MetaData()

    utenti = Table('utenti',metadata,
               Column('id_utente',Integer,autoincrement=True),
               Column('nome',String(25)),
               Column('cognome',String(25)),
               Column('email',String(30)),
               Column('telefono',String(15)),
               Column('password',String(16),nullable=False),
               Column('tampone',Boolean),
               PrimaryKeyConstraint('id_utente',name='utenti_pk'),
               Column('ruolo',Enum(Ruoli))
               )

    #TODO: aggiungere colonne istruttore id e istruttre
    corsi = Table('corsi',metadata,
              Column('id_corso', Integer,autoincrement=True),
              Column('nome', String(25)),
              PrimaryKeyConstraint('id_corso','nome',name='corsi_pk'),
              Column('descrizione', String(150)),
              Column('istruttore',None,ForeignKey('utenti.id_utente'))
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

    prenotazioni= Table('prenotazioni',metadata,
                        Column('utente',None,ForeignKey('utenti.id_utente'),
                               nullable=False),
                        Column('corso',None,ForeignKey('corsi.id_corso'),
                               nullable=False),
                        Column('lezione',None,ForeignKey('lezioni.id_lezione'))
                        )

    metadata.create_all(engine)


    query = text("CREATE ROLE IF NOT EXISTS :x,:y,:z,:c")
    con.execute(query, {"x": "Anonimo", "y": "Gestore", "z": "Istruttore", "c": "Cliente"})

    query = text("GRANT INSERT,DELETE,UPDATE ON gym.* to :x")
    con.execute(query, {"x": "Gestore"})

    # Istruttre
    query = text("GRANT INSERT,DELETE,UPDATE ON gym.corsi to :x")
    con.execute(query, {"x": "Istruttore"})

    query = text("GRANT INSERT,DELETE,UPDATE ON gym.lezioni to :x")
    con.execute(query, {"x": "Istruttore"})

    query = text("GRANT INSERT,DELETE,UPDATE ON gym.utenti to :x")
    con.execute(query, {"x": "Cliente"})

    query = text("GRANT INSERT,DELETE,UPDATE ON gym.corsi to :x")
    con.execute(query, {"x": "Cliente"})

    query = text("GRANT INSERT,DELETE,UPDATE ON gym.corsi_seguiti to :x")
    con.execute(query, {"x": "Cliente"})

    con.execute("set global activate_all_roles_on_login = on")  # attivazione di tutti i ruoli  (da decommentare dopo!)


    con=engine.connect()