from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import db
from db import create_engine

engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")

base = automap_base()
base.prepare(engine, reflect=True)

utenti_orm = base.classes.utenti

lezioni_orm = base.classes.lezioni

corsi_orm = base.classes.corsi
#corsi_seguiti_orm = base.classes.corsi_seguiti

locali_orm = base.classes.locali

#prenotazioni_orm = base.classes.prenotazioni

session = Session(engine)




