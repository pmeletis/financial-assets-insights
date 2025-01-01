import time
from datetime import date
from functools import partial
from pathlib import Path
from typing import Literal, Optional
from typing_extensions import deprecated
from typing import TypeAlias
# from warnings import deprecated # Python 3.13 onwards

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from urllib.error import HTTPError

URL: TypeAlias = str
URL_ASSETS = 'https://raw.githubusercontent.com/pmeletis/fai-dumps/main/'

INFO = pd.DataFrame({
    'yf_symbol': ['^GSPC', '^NDX', '^N100', '^RUT', '^IXIC', '^NYA', 'BTC-USD', 'ETH-USD'],
    'filename_prefix': ['sp500', 'nasdaq100', 'euronext100', 'russel2000', 'nasdaq_comp', 'nyse_comp', 'btcusd', 'ethusd'],
    'button_name': ['S&P 500', 'NASDAQ 100', 'EURONEXT 100', 'RUSSEL 2000', 'NASDAQ Composite', 'NYSE Composite', 'BTCUSD', 'ETHUSD'],
    # 'legend_name': [],
    'button_default': [True, True, True, True, False, False, True, True],
    'button_selection': [True, True, True, True, False, False, True, True],
})


def download_and_save_data(dirpath: Path, tts=3):
  current_date_str = date.today().strftime('%Y%m%d')
  dirpath = dirpath / current_date_str
  dirpath.mkdir()
  for symbol, prefix, _, _, _ in INFO.itertuples(index=False):
    df = yf.download(symbol, start='1927-01-01')
    df.to_csv(dirpath / f'{current_date_str}-{prefix}-daily.csv')
    time.sleep(3)


def _get_most_recent(dirpath: Path, prefix):
  filepaths = dirpath.glob(f'{prefix}_*.csv')
  dates = [fp.name[-12:-4] for fp in filepaths]
  if dates:
    most_recent_date = sorted(dates)[-1]
    return dirpath / f'{prefix}_{most_recent_date}.csv'


@st.cache_data
def get_close_data_from_dumps(date_str: str = '20240904'):
  reader_fn = partial(pd.read_csv, parse_dates=['Date'], index_col='Date')

  # TODO(panos): handle http error 404 not found

  dfs = dict()
  for name in INFO['filename_prefix']:
    url = URL_ASSETS + date_str + f'/{date_str}-{name}-daily.csv'
    try:
      df = reader_fn(url)
    except HTTPError as e:
      if e.code == 404:
        print(f"Error 404: The requested URL {url} was not found on the server.")
      else:
        print(f"HTTP Error: {e.code}")
      continue
    except Exception as e:
      print(f"Unknown error: {e.reason}")
      continue
    else:
      dfs[name] = df['Close']

  # aggregate data and delete latest day to be sure all symbols
  # have no-NaN latest value
  daily_close = pd.DataFrame(dfs)
  daily_close = daily_close[:-1]

  # fill in gaps
  daily_close = daily_close.ffill()

  return daily_close


def get_close_data_from_dir(dirpath: Path):

  reader_fn = partial(pd.read_csv, parse_dates=['Date'], index_col='Date')

  dfs = dict()
  for p in dirpath.glob('*.csv'):
    name = p.name.split(sep='-')[1]
    dfs[name] = reader_fn(p)['Close']

  # aggregate data and delete latest day to be sure all symbols
  # have no-NaN latest value
  daily_close = pd.DataFrame(dfs)
  daily_close = daily_close[:-1]

  return daily_close


@st.cache_data
def get_latest_close_data_from_dir(dirpath: Path = Path()):
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
  assert isinstance(signal, pd.Series)
  signal = signal.copy()
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
  """How many times a change larger than 'change' has occured.
  """
  assert isinstance(signal, pd.Series)
  # get rid of any NaNs in the beginning
  signal = signal[signal.first_valid_index():]
  # it can be that S&P does not have values for the weekend days
  signal = signal.ffill()

  frac_change = signal.pct_change()[1:] # the first element is NaN
  pct_change = frac_change * 100

  num_occurences = pct_change >= change if change > 0 else pct_change <= change
  num_occurences = np.count_nonzero(num_occurences)

  return num_occurences


def days_since_change(signal: pd.Series, change, days_period: int = 1,
                      return_pct_change=False, return_num_occurences=False):
  """Days since at least a percentage `change`.

  Args:
    change: percentage change, eg. 2 for 2%, or -1 for -1%
    days_period: number of days to accumulate for the change

  Return:
    num_days_since_change: pd.Series
    pct_change: pd.Series
    num_occurences: int
  """
  assert isinstance(signal, pd.Series)
  assert isinstance(days_period, int) and days_period >= 1
  # get rid of any NaNs in the beginning
  signal = signal[signal.first_valid_index():]
  # it can be that S&P does not have values for the weekend days
  signal = signal.ffill()

  frac_change = signal.pct_change(periods=days_period)[1:] # the first element is NaN
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


@st.cache_data
def batch_process(daily_close: pd.DataFrame):
  """Process everything in one function to reduce computations.
  """
  supported_column_names = set(INFO['filename_prefix'])
  if len(new_cols := set(daily_close.columns) - supported_column_names) > 0:
    raise ValueError(f'unexpected columns in `daily_close`: {new_cols}.')

  dsath = daily_close.apply(days_since_ath)

  return dsath


@st.cache_data
@deprecated('Use the get_close_data_from_* functions.')
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


@st.cache_data
def get_close_data_by_symbol(symbol_name: str, symbol_source: Path | URL) -> pd.Series:
  if symbol_name not in ['^FTW5000', '^NDX', '^SPX', '^SPXEW']:
    raise ValueError()

  if isinstance(symbol_source, Path) and symbol_source.exists() and symbol_source.is_dir():
    df = pd.read_csv(symbol_source / f'{symbol_source.name}-{symbol_name[1:].lower()}-daily.csv',
                     parse_dates=['Date'])
    df.columns = df.columns.str.lower()
    df = df.set_index('date')
    return df['close']
  else:
    raise NotImplementedError(f'Getting data for {symbol_name} from {symbol_source} is not implemented.')

@st.cache_data
def get_ratios_df(dropna: False | Literal['all', 'any'] = 'all',
                  long_format: bool = False,
                  subsample_step: int = 1,
                  append_date_column: bool = False) -> pd.DataFrame:
  """
  Args:
    subsample_step: The step to subsample the data. Default is 1, meaning no subsampling.
    append_date_column: If True, a 'date' column is appended to the DataFrame.
      Does not apply if `long_format` is True.
  """
  ftw5000 = get_close_data_by_symbol('^FTW5000', Path('datasets/20241203'))
  spx = get_close_data_by_symbol('^SPX', Path('datasets/20241203'))
  ndx = get_close_data_by_symbol('^NDX', Path('datasets/20241203'))
  spxew = get_close_data_by_symbol('^SPXEW', Path('datasets/20241203'))

  spx_ftw5000 = spx / ftw5000
  ndx_spx = ndx / spx
  spx_spxew = spx / spxew

  ratios_df = pd.concat({'spx/ftw5000': spx_ftw5000, 'ndx/spx': ndx_spx, 'spx/spxew': spx_spxew},
                        axis=1, verify_integrity=True)

  if dropna is not False:
    first_valid_index = ratios_df.dropna(how=dropna).index[0]
    ratios_df = ratios_df.loc[first_valid_index:]

  ratios_df = ratios_df.iloc[::subsample_step, :]

  if append_date_column:
    ratios_df['date'] = ratios_df.index

  if long_format:
    ratios_df = ratios_df.reset_index().melt(id_vars=['date'], var_name='metric', value_name='value')

  return ratios_df
