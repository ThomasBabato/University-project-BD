import enum

from sqlalchemy import create_engine, MetaData, inspect, ForeignKeyConstraint, PrimaryKeyConstraint, select
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean,Enum,text
from  sqlalchemy_utils.functions import database
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

class Ruoli(enum.Enum):
    Gestore=1
    Istruttore=2
    Cliente=3
    Anonimo=4

def set_istruttore():
    return 2


def create_db(nome,paswd):
    engine = create_engine("mysql+pymysql://"+nome+":"+paswd+"@localhost", echo=False)
    con = engine.connect()
    con.execute("create database if not exists gym ")
    if database.database_exists("mysql+pymysql://"+nome+":"+paswd+"@localhost/gym"):
        con = engine.connect()
        con.execute("commit")
        con.execute("create database if not exists gym ")

        engine = create_engine("mysql+pymysql://"+nome+":"+paswd+"@localhost/gym")
        metadata = MetaData()

        utenti = Table('utenti',metadata,
                   Column('id_utente',Integer,primary_key=True,autoincrement=True),
                   Column('nome',String(25)),
                   Column('cognome',String(25)),
                   Column('email',String(30)),
                   Column('telefono',String(15)),
                   Column('password',String(16),nullable=False),
                   Column('tampone',Boolean),
                   Column('ruolo',Enum(Ruoli))
                   )

        corsi = Table('corsi',metadata,
                  Column('id_corso', Integer,autoincrement=True),
                  Column('nome', String(25)),
                  PrimaryKeyConstraint('id_corso','nome',name='corsi_pk'),
                  Column('descrizione', String(150)),
                  Column('istruttore',None,ForeignKey('utenti.id_utente',ondelete="CASCADE"),nullable=True),
                  Column('locale',None,ForeignKey('locali.id_locale'))
                  )

        Base = declarative_base()
        corsi_seguiti = Table('corsi_seguiti',metadata,
                        Column('utente',ForeignKey('utenti.id_utente',ondelete="Cascade")),
                        Column('corso_id',ForeignKey('corsi.id_corso',ondelete="Cascade")),
                        )


        locali = Table('locali',metadata,
                       Column('id_locale', Integer, primary_key=True, autoincrement=True),
                       Column('nome', String(25)),
                       Column('mq', Float),
                       Column('capienza_massima', Integer)
                      )

        lezioni = Table('lezioni',metadata,
                        Column('id_lezione', Integer, primary_key=True, autoincrement=True),
                        Column('codice_corso', ForeignKey('corsi.id_corso',ondelete="Cascade"),nullable=False),
                        Column('descrizione', String(120)),
                        Column('Data_e_ora',DateTime), #formato yy/mm/gg hh/mm
                        Column('persone_consentite',Integer)
                        )

        prenotazioni= Table('prenotazioni',metadata,
                            Column('utente',None,ForeignKey('utenti.id_utente',ondelete="Cascade"),
                                   nullable=False),
                            Column('corso',None,ForeignKey('corsi.id_corso',ondelete="Cascade"),
                                   nullable=False),
                            Column('lezione',None,ForeignKey('lezioni.id_lezione',ondelete="Cascade"))
                            )

        metadata.create_all(engine)



        con.execute("CREATE ROLE IF NOT EXISTS 'Anonimo'@'localhost'")
        con.execute("CREATE ROLE IF NOT EXISTS 'Cliente'@'localhost'")
        con.execute("CREATE ROLE IF NOT EXISTS 'Istruttore'@'localhost'")
        con.execute("CREATE ROLE IF NOT EXISTS 'Gestore'@'localhost'")

        con.execute("set Default Role all to 'Anonimo'@'localhost','Gestore'@'localhost','Istruttore'@'localhost','Cliente'@'localhost' ")

        con.execute("GRANT INSERT on gym.utenti to 'Anonimo'@'localhost'")

        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.* to 'Gestore'@'localhost'")

        # Istruttre
        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.corsi to 'Istruttore'@'localhost'")

        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.lezioni to 'Istruttore'@'localhost'")

        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.utenti to 'Cliente'@'localhost'")

        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.corsi to 'Cliente'@'localhost'")


        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.corsi_seguiti to 'Cliente'@'localhost'")

        con.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON gym.prenotazioni to 'Cliente'@'localhost'")

        con.execute("set global activate_all_roles_on_login = on")  # attivazione di tutti i ruoli  (da decommentare dopo!)

        return utenti,locali,lezioni,corsi_seguiti,engine,corsi,prenotazioni,con
