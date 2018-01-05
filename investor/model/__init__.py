import enum
from sqlalchemy import Column, Integer, Float, String, DateTime, TIMESTAMP, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
Base = declarative_base()


class MarketType(enum.Enum):
    coin = 1
    forex = 2
    stock = 3


class Market(Base):
    __tablename__ = 'markets'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(Enum(MarketType))
    created = Column(TIMESTAMP, default=func.now())
    __table_args__ = (UniqueConstraint('name', 'type', name='name_type_idx'),)


class Pair(Base):
    __tablename__ = 'pairs'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    created = Column(TIMESTAMP, default=func.now())


class MarketPair(Base):
    __tablename__ = 'market_pairs'
    id = Column(Integer, primary_key=True)
    market_id = Column(Integer, ForeignKey('markets.id'))
    pair_id = Column(Integer, ForeignKey('pairs.id'))
    name = Column(String(255))
    created = Column(TIMESTAMP, default=func.now())
    market = relationship("Market", backref="market_pairs")
    pair = relationship("Pair", backref="market_pairs")
    __table_args__ = (UniqueConstraint('market_id', 'pair_id', name='market_pair_idx'),)


class Trade(Base):
    __tablename__ = 'trades'
    market_pair_id = Column(Integer, ForeignKey('market_pairs.id'), primary_key=True)
    ts = Column(DateTime, primary_key=True)
    created = Column(TIMESTAMP, default=func.now())


class TradeMinute(Base):
    __tablename__ = 'trade_minutes'
    market_pair_id = Column(Integer, primary_key=True)
    ts = Column(DateTime, primary_key=True)
    price = Column(Float(precision=10, asdecimal=True))
    volume = Column(Float(precision=10, asdecimal=True))
    num = Column(Integer)
    created = Column(TIMESTAMP, default=func.now())


