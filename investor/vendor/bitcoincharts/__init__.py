import requests
from os.path import basename, exists, join
import urllib.request
import sys
import gzip
import time
import arrow
from itertools import groupby
import decimal


def progress(block_count: int, block_size: int, total_size: int):
    percentage = 100. * block_count * block_size / total_size
    print("%.2f%% ( %d KB )\r" % (percentage, total_size / 1024), end='', file=sys.stdout)


class BitcoinCharts:
    root_url = 'http://api.bitcoincharts.com/'

    @classmethod
    def _parse_csv_row(cls, row):
        row[0] = int(row[0])
        row[1] = row[1].rstrip('0').rstrip('.')
        row[2] = row[2].rstrip('0').rstrip('.')
        return dict(zip(('ts', 'price', 'amount'), row))

    def download_history_trades(self, exchange: str, currency: str, download_dir: str):
        """

        :param exchange: bitflyer/coincheck/zaif
        :param currency: JPY
        :param download_dir: resources
        :return: download file name
        """

        root_url = self.root_url
        symbol = '{exchange}{currency}'.format(**locals())
        url = '{root_url}/v1/csv/{symbol}.csv.gz'.format(**locals())
        fname = basename(url)
        urllib.request.urlretrieve(url, fname, reporthook=progress)
        return fname

    def get_latest_trades(self, exchange: str, currency: str, ts: int = None, recursive = False, sleep_secs: int = 60):
        """
        tsがないと最新の2000件で順番が新しい順になる
        tsを指定した場合はtsより新しいものを取得

        :param exchange: bitflyer/coincheck/zaif
        :param currency: JPY
        :param ts: epoch
        :param sleep_secs:
        :return: json object
        """
        symbol = '{exchange}{currency}'.format(**locals())
        root_url = self.root_url
        url = '{root_url}/v1/trades.csv?symbol={symbol}'.format(**locals())

        def _get_latest_trades(u: str, t: int):
            u += '&start={0}'.format(t)
            res = requests.get(u)
            for r in res.text.split('\n'):
                yield self._parse_csv_row(r)

        while True:
            for row in _get_latest_trades(url, ts):
                ts = row['ts'] + 1
                yield row
            if not recursive:
                break
            time.sleep(sleep_secs)

    def get_full_trades(self, exchange: str, currency: str, download_dir: str, sleep_secs: int = 10):
        """
        すべてのデータを取得

        :param exchange: bitflyer/coincheck/zaif
        :param currency: JPY
        :param download_dir:
        :param sleep_secs:
        :return: json object
        """
        symbol = '{exchange}{currency}'.format(**locals())
        fname = join(download_dir, '{symbol}.csv.gz'.format(**locals()))
        if not exists(fname):
            fname = self.download_history_trades(exchange, currency, download_dir)

        ts = 0
        with gzip.open(fname, 'rt') as f:
            for r in f:
                r = self._parse_csv_row(r)
                ts = r['ts']
                yield r

        yield from self.get_latest_trades(exchange, currency, ts=ts + 1, recursive=True, sleep_secs=sleep_secs)

    def get_1min_agg_trades(self, exchange: str, currency: str, ts: int = None,
                            recursive: bool = False, download_dir: str = None, sleep_secs: int = 60):
        decimal.getcontext().prec = 10
        if ts:
            it = self.get_latest_trades(exchange, currency, ts, recursive, sleep_secs)
        else:
            if not download_dir or not exists(download_dir):
                raise FileNotFoundError('download dir is not exists: %s' % download_dir)
            it = self.get_full_trades(exchange, currency, download_dir, sleep_secs)

        for ts, group in groupby(it, key=lambda r: arrow.get(r['ts']).floor('minute').timestamp):
            stats = {'ts': ts, 'open': 0, 'high': 0, 'low': 0, 'close': 0, 'amount': 0, 'num': 0}
            for i, row in enumerate(group):
                price = decimal.Decimal(row['price'])
                amount = decimal.Decimal(row['amount'])
                stats['num'] += 1
                stats['amount'] += amount
                stats['close'] = price
                if i == 0:
                    stats['open'] = price
                    stats['high'] = price
                    stats['low'] = price
                elif stats['high'] < price:
                    stats['high'] = price
                elif stats['low'] > price:
                    stats['low'] = price
            for c in ('open', 'high', 'low', 'close', 'amount'):
                stats[c] = str(stats[c])
            yield stats







