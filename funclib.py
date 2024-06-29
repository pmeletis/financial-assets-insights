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
from urllib.error import HTTPError

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
def get_close_data_from_dumps(date_str: str = '20240621'):
  reader_fn = partial(pd.read_csv, parse_dates=['Date'], index_col='Date')

  # TODO(panos): handle http error 404 not found

  url_sp = URL_ASSETS + f's%26p500_daily_{date_str}.csv'
  sp500_daily = reader_fn(url_sp)

  url_nc = URL_ASSETS + f'nasdaq_comp_daily_{date_str}.csv'
  nasdaq_comp_daily = reader_fn(url_nc)

  url_r2 = URL_ASSETS + f'russel2000_daily_{date_str}.csv'
  russel2000_daily = reader_fn(url_r2)

  # aggregate data
  indices_all_daily_close = pd.DataFrame({'S&P500': sp500_daily['Close'],
                                          'NASDAQ Comp': nasdaq_comp_daily['Close'],
                                          'RUSSEL2000': russel2000_daily['Close']})

  # read BTC optionally
  url_btc = URL_ASSETS + f'btcusd_daily_{date_str}.csv'
  try:
    btcusd_daily = reader_fn(url_btc)
  except HTTPError as e:
    if e.code == 404:
      print(f"Error 404: The requested URL {url_btc} was not found on the server.")
    else:
      print(f"HTTP Error: {e.code}")
  except Exception as e:
    print(f"Unknown error: {e.reason}")
  else:
    indices_all_daily_close['BTCUSD'] = btcusd_daily['Close']

  # delete latest day to be sure all indices have no-NaN latest value
  indices_all_daily_close = indices_all_daily_close[:-1]

  return indices_all_daily_close


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


def _num_occurences(signal: pd.Series, change):
  
  # get rid of any NaNs in the beginning
  signal = signal[signal.first_valid_index():]
  # it can be that S&P does not have values for the weekend days
  signal = signal.ffill()

  frac_change = signal.pct_change()[1:] # the first element is NaN
  pct_change = frac_change * 100

  num_occurences = pct_change >= change if change > 0 else pct_change <= change
  num_occurences = np.count_nonzero(num_occurences)

  return num_occurences

def days_since_change(signal: pd.Series, change, return_pct_change=False, return_num_occurences=False):
  """Days since at least a percentage `change`.

  Args:
    change: percentage change, eg. 2 for 2%, or -1 for -1%

  Return:
    num_days_since_change: pd.Series
    pct_change: pd.Series
    num_occurences: int
  """
  # get rid of any NaNs in the beginning
  signal = signal[signal.first_valid_index():]
  # it can be that S&P does not have values for the weekend days
  signal = signal.ffill()

  frac_change = signal.pct_change()[1:] # the first element is NaN
  pct_change = frac_change * 100

  num_days_since_change = [0]
  for i, c in enumerate(pct_change):
    if (change > 0 and c < change) or (change < 0 and c > change):
      num_days_since_change.append(num_days_since_change[i] + 1)
    else:
      num_days_since_change.append(0)
  num_days_since_change = pd.Series(num_days_since_change, index=signal.index, dtype=np.int32)

  num_occurences = pct_change >= change if change > 0 else pct_change <= change
  num_occurences = np.count_nonzero(num_occurences)

  rets = (num_days_since_change,)

  if return_pct_change:
    rets = rets + (pct_change,)

  if return_num_occurences:
    rets = rets + (num_occurences,)

  return rets[0] if len(rets) == 1 else rets
