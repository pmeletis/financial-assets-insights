import time
from datetime import date
from functools import partial
from pathlib import Path
from typing import Optional

# import matplotlib.patches as patches
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

URL_ASSETS = 'https://raw.githubusercontent.com/pmeletis/fai-dumps/main/'


def download_and_save_data(dirpath: Path):
  current_date = date.today().strftime('%Y%m%d')
  # fetch data with maximum duration
  hist = yf.download('^IXIC', start='1927-01-01') # '^IXIC' for Nasdaq Composite
  hist.to_csv(dirpath / f'nasdaq_comp_daily_{current_date}.csv')
  time.sleep(2)
  hist = yf.download('^GSPC', start='1927-01-01') # ^GSPC' for S&P 500
  hist.to_csv(dirpath / f's&p500_daily_{current_date}.csv')
  time.sleep(2)
  hist = yf.download('^RUT', start='1927-01-01') # for Russel 2000
  hist.to_csv(dirpath / f'russel2000_daily_{current_date}.csv')
  time.sleep(2)
  hist = yf.download('BTC-USD', start='1927-01-01') # for Bitcoin
  hist.to_csv(dirpath / f'btcusd_daily_{current_date}.csv')


def _get_most_recent(dirpath: Path, prefix):
  filepaths = dirpath.glob(f'{prefix}_*.csv')
  dates = [fp.name[-12:-4] for fp in filepaths]
  if dates:
    most_recent_date = sorted(dates)[-1]
    return dirpath / f'{prefix}_{most_recent_date}.csv'


@st.cache_data
def get_latest_close_data(dirpath: Path = Path()):
  """Get data from local dir or download from online."""
  # TODO(panos): handle better

  reader_fn = partial(pd.read_csv, parse_dates=['Date'], index_col='Date')

  filepath_sp = _get_most_recent(dirpath, 's&p500_daily')
  url_sp = URL_ASSETS + 's%26p500_daily_20240322.csv'
  if filepath_sp is not None:
    sp500_daily = reader_fn(filepath_sp)
  else:
    sp500_daily = reader_fn(url_sp)

  filepath_nc = _get_most_recent(dirpath, 'nasdaq_comp_daily')
  url_nc = URL_ASSETS + 'nasdaq_comp_daily_20240322.csv'
  if filepath_nc is not None:
    nasdaq_comp_daily = reader_fn(filepath_nc)
  else:
    nasdaq_comp_daily = reader_fn(url_nc)

  filepath_r2 = _get_most_recent(dirpath, 'russel2000_daily')
  url_r2 = URL_ASSETS + 'russel2000_daily_20240322.csv'
  if filepath_nc is not None:
    russel2000_daily = reader_fn(filepath_r2)
  else:
    russel2000_daily = reader_fn(url_r2)

  filepath_btc = _get_most_recent(dirpath, 'btcusd_daily')
  url_btc = URL_ASSETS + 'btcusd_daily_20240322.csv'
  if filepath_nc is not None:
    btcusd_daily = reader_fn(filepath_btc)
  else:
    btcusd_daily = reader_fn(url_btc)

  # aggregate data
  indices_all_daily_close = pd.DataFrame({'S&P500': sp500_daily['Close'],
                                          'NASDAQ Comp': nasdaq_comp_daily['Close'],
                                          'RUSSEL2000': russel2000_daily['Close'],
                                          'BTCUSD': btcusd_daily['Close']})
  # delete latest day to be sure all indices have no-NaN value
  indices_all_daily_close = indices_all_daily_close[:-1]

  return indices_all_daily_close


def days_since_ath(signal: pd.Series, eps: Optional[float] = None):
  # get rid of any NaNs in the beginning
  signal = signal[signal.first_valid_index():]
  # it can be that S&P does not have values for the weekend days
  signal = signal.ffill()
  # assert not signal.isna().any(), (signal.name, signal.first_valid_index())
  assert eps is None or (isinstance(eps, float) and eps >= 0.0)
  ath = signal.iloc[0]
  num_days_since_ath = [0]
  eps = eps or 0
  for i, price in enumerate(signal[1:]):
    diff = ath - price
    if diff < eps:
      ath = max(ath, price)
      num_days_since_ath.append(0)
    else:
      num_days_since_ath.append(num_days_since_ath[-1] + 1)
  num_days_since_ath = pd.Series(num_days_since_ath, index=signal.index, dtype=np.int32)
  return num_days_since_ath
