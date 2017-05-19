# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, scoped_session


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    nick = Column(String(100), nullable=False)
    ip_address = Column(String(15), nullable=False)
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=True)

    def __init__(self, nick, ip_address):
        self.nick = nick
        self.ip_address = ip_address

class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=True)
    description = Column(String(100), nullable=True)
    users = relationship('User', backref='channel')

    def __init__(self, name, password, description):
        self.name = name
        self.password = password
        self.description = description


class Black_IP(Base):
    __tablename__ = 'black_ip'
    id = Column(Integer, primary_key=True)
    ip = Column(String(15), nullable=False)
    cause = Column(String(100), nullable=True)

    def __init__(self, ip, cause):
        self.ip = ip
        self.cause = cause

class Black_Nick(Base):
    __tablename__ = 'black_nick'
    id = Column(Integer, primary_key=True)
    nick = Column(String(100), nullable=False)
    cause = Column(String(100), nullable=True)

    def __init__(self, nick, cause):
        self.nick = nick
        self.cause = cause


def database_connect():
    engine = create_engine('sqlite:///database.db')
    connection = engine.connect()
    
    
    if engine.has_table("User"):
        User.__table__.drop(engine)
        Channel.__table__.drop(engine)
        Black_IP.__table__.drop(engine)
        Black_Nick.__table__.drop(engine)
    

    # create tables
    Base.metadata.create_all(engine)
    # create session
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    test_data_for_database(session)
    return session

def test_data_for_database(session):
    session.add_all([
                        User("Marek", "192.168.1.10"),
                        User("Jozek", "192.168.1.11"),
                        User("Weronika", "192.168.1.12"),
                        User("Mietek", "192.168.123.123")
        ])
    session.commit()

    session.add_all([
                        Channel("Muzyka", "muzyka", "Kanał o muzyce"),
                        Channel("Informatyka", "informatyka", "Kanał o informatyce"),
                        Channel("Studia", None, "Kanał o studiach")      
        ])
    session.commit()
 
def test_print(session):
    u = session.query(User).all()
    for i in u:
        print(i.nick)
    
    c = session.query(Channel).all()
    for j in c:
        print(j.name)

if __name__ == "__main__": 
    con = database_connect()
    test_data_for_database(con)
    #test_print(con)