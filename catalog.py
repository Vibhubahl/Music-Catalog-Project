from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup1 import Base, MusicType, MusicName, User

engine = create_engine('sqlite:///musicitemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create dummy user
name1 = MusicType(id=0, name="English")
session.add(name1)
session.commit()

music1 = MusicName(name="Thank u, next", artist="Ariana Grande\
    ", releaseyear="2019", music_type=name1, musicname_id=0)
session.add(music1)
session.commit()

name2 = MusicType(id=1, name="Hindi")
session.add(name2)
session.commit()

music6 = MusicName(name="Apna Time Aayega", artist="Ranveer Singh\
    ", releaseyear="2019", music_type=name2, musicname_id=1)
session.add(music6)
session.commit()

name3 = MusicType(id=2, name="Punjabi")
session.add(name3)
session.commit()

music15 = MusicName(name="She Don't Know", artist="Millind Gaba\
    ", releaseyear="2019", music_type=name3, musicname_id=2)
session.add(music15)
session.commit()

print "added names!"
