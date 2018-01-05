#!/usr/bin/env python3.6
import sys
from os.path import abspath, dirname
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session

sys.path.append(dirname(dirname(abspath(__file__))))
from investor import config
from investor.model import *


def load_initial_data(session: Session):
    session.execute('SET FOREIGN_KEY_CHECKS = 0')
    session.execute('truncate {}'.format(Market.__tablename__))
    session.execute('truncate {}'.format(Pair.__tablename__))
    session.execute('truncate {}'.format(MarketPair.__tablename__))
    session.execute('SET FOREIGN_KEY_CHECKS = 1')
    session.commit()

    markets = [
        Market(name='bitflyer', type='coin'),
        Market(name='coincheck', type='coin'),
        Market(name='zaif', type='coin'),
        Market(name='binnance', type='coin'),
        Market(name='dmm', type='forex'),
    ]
    session.add_all(markets)
    session.commit()

    pairs = [
        Pair(name='BTCJPY'),
        Pair(name='ETHJPY'),
        Pair(name='ETHBTC'),
        Pair(name='BTCUSD'),
        Pair(name='USDJPY'),
        Pair(name='EURJPY'),
        Pair(name='AUDJPY'),
        Pair(name='EURUSD'),
    ]
    session.add_all(pairs)
    session.commit()

    market_pairs = [
        MarketPair(name='bitflyerBTC', market=markets[0], pair=pairs[0]),
        MarketPair(name='coincheckBTC', market=markets[1], pair=pairs[0]),
        MarketPair(name='zaifBTC', market=markets[2], pair=pairs[0]),
    ]
    session.add_all(market_pairs)
    session.commit()


def main():
    engine = sqlalchemy.create_engine(config.SQLALCHEMY_ENGINE)
    Base.metadata.create_all(bind=engine)

    s = sessionmaker(bind=engine)
    load_initial_data(s())


if __name__ == '__main__':
    main()
