import glob
import time
from datetime import date
from functools import partial
from pathlib import Path
from typing import Optional

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


URL_ASSETS = Path('https://github.com/pmeletis/financial-assets-insights/files')


def download_and_save_data(dirpath: Path):
  current_date = date.today().strftime('%Y%m%d')
  # fetch data with maximum duration
  hist = yf.download('^IXIC', start='1927-01-01') # '^IXIC' for Nasdaq Composite
  hist.to_csv(dirpath / f'nasdaq_comp_daily_{current_date}.csv')
  time.sleep(1)
  hist = yf.download('^GSPC', start='1927-01-01') # ^GSPC' for S&P 500
  hist.to_csv(dirpath / f's&p500_daily_{current_date}.csv')
  time.sleep(1)
  hist = yf.download('^RUT', start='1927-01-01') # for Russel 2000
  hist.to_csv(dirpath / f'russel2000_daily_{current_date}.csv')


def get_latest_close_data(dirpath: Path = Path()):
  """Get data from local dir or download from online."""
  # TODO(panos): handle better

  # format *_YYYYMMDD.csv
  filepaths = dirpath.glob('*.csv')
  dates = [fp.name[-12:-4] for fp in filepaths]
  most_recent_date = sorted(dates)[-1]
  reader_fn = partial(pd.read_csv, parse_dates=['Date'], index_col='Date')

  filepath_sp = dirpath / f"s&p500_daily_{most_recent_date}.csv"
  url_sp = URL_ASSETS / '14212769/s.p500_daily_20240208.csv'
  if filepath_sp.exists():
    sp500_daily = reader_fn(filepath_sp)
  else:
    sp500_daily = reader_fn(url_sp)

  filepath_nc = dirpath / f"nasdaq_comp_daily_{most_recent_date}.csv"
  url_nc = URL_ASSETS / '14212775/nasdaq_comp_daily_20240208.csv'
  if filepath_nc.exists():
    nasdaq_comp_daily = reader_fn(filepath_nc)
  else:
    nasdaq_comp_daily = reader_fn(url_nc)


  filepath_r2 = dirpath / f"russel2000_daily_{most_recent_date}.csv"
  url_r2 = URL_ASSETS / '14212780/russel2000_daily_20240208.csv'
  if filepath_nc.exists():
    russel2000_daily = reader_fn(filepath_r2)
  else:
    russel2000_daily = reader_fn(url_r2)

  # aggregate data
  indices_all_daily_close = pd.DataFrame({'S&P500': sp500_daily['Close'],
                                          'NASDAQ Comp': nasdaq_comp_daily['Close'],
                                          'RUSSEL2000': russel2000_daily['Close']})
  # delete latest day to be sure all indices have no-NaN value
  indices_all_daily_close = indices_all_daily_close[:-1]
  return indices_all_daily_close


def days_since_ath(signal: pd.Series, eps: Optional[float] = None):
  signal = signal[signal.first_valid_index():]
  assert not signal.isna().any()
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
  num_days_since_ath = pd.Series(num_days_since_ath, index=signal.index)
  return num_days_since_ath
