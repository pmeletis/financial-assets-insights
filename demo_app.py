import streamlit as st
import pandas as pd
import numpy as np

st.title('Insights of Financial Markets')

st.subheader('Indices')

# import numpy as np
import matplotlib.pyplot as plt
# import pandas as pd
from typing import Optional
# import yfinance as yf
from datetime import date
from pathlib import Path
from functools import partial
# import mpld3
# import streamlit.components.v1 as components

DIRPATH_DATASET = Path.absolute(Path('.')) / 'datasets'

data_load_state = st.text('Loading data...')

current_date = date.today().strftime('%Y%m%d')
reader_fn = partial(pd.read_csv, parse_dates=['Date'], index_col='Date')
sp500_daily = reader_fn(DIRPATH_DATASET / f"s&p500_daily_{current_date}.csv")
nasdaq_comp_daily = reader_fn(DIRPATH_DATASET / f"nasdaq_comp_daily_{current_date}.csv")
russel2000_daily = reader_fn(DIRPATH_DATASET / f"russel2000_daily_{current_date}.csv")
# aggregate data
indices_all_daily_close = pd.DataFrame({'S&P500': sp500_daily['Close'],
                                        'NASDAQ Comp': nasdaq_comp_daily['Close'],
                                        'RUSSEL2000': russel2000_daily['Close']})

data_load_state.text('Loading data... done!')

# st.write(sp500_daily)

# st.line_chart(indices_all_daily_close)

data_load_state.text('Creating graphs...')

fig = plt.figure(figsize=(14, 7), dpi=300)
plt.plot(sp500_daily['Close'], label='S&P 500')
plt.hlines(sp500_daily['Close'].iloc[-1], sp500_daily.index[0], sp500_daily.index[-1], linestyles='--', alpha=0.3, zorder=-1)
lines = plt.plot(nasdaq_comp_daily['Close'], label='NASDAQ Composite')[0]
plt.hlines(nasdaq_comp_daily['Close'].iloc[-1], sp500_daily.index[0], sp500_daily.index[-1], linestyles='--', alpha=0.3, colors=lines.get_color(), zorder=-1)
lines = plt.plot(russel2000_daily['Close'], label='Russel 2000')[0]
plt.hlines(russel2000_daily['Close'].iloc[-1], sp500_daily.index[0], sp500_daily.index[-1], linestyles='--', alpha=0.3, colors=lines.get_color(), zorder=-1)
plt.yscale('log')
plt.xlabel('Date')
plt.tight_layout()
plt.legend()
st.pyplot(fig=fig)

data_load_state.text('Creating graphs... done!')

def days_since_ath(signal: pd.Series, eps: Optional[float] = None):
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
  return num_days_since_ath

dsath_sp = days_since_ath(sp500_daily['Close'])
dsath_nc = days_since_ath(nasdaq_comp_daily['Close'])
dsath_r2 = days_since_ath(russel2000_daily['Close'])
top_limit = max(*dsath_sp[-2*365:], *dsath_nc[-2*365:], *dsath_r2[-2*365:])

fig, _ = plt.subplots(ncols=2, figsize=(12,5), width_ratios=(3, 1))
plt.subplot(1, 2, 1)
plt.plot(sp500_daily.index, dsath_sp, label='S&P 500')
plt.hlines(dsath_sp[-1], sp500_daily.index[0], sp500_daily.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
plt.plot(nasdaq_comp_daily.index, dsath_nc, alpha=0.6, label='NASDAQ Composite')
plt.plot(russel2000_daily.index, dsath_r2, alpha=0.3, label='Russel 2000')
plt.ylabel('Days since latest ATH')
plt.xlabel('Date')
plt.legend()
# rect = patches.Rectangle((plt.xlim()[1]-100, 0), 40, top_limit, linewidth=1, edgecolor='r', facecolor='none')
# plt.gca().add_patch(rect)
plt.subplot(1, 2, 2)
plt.plot(sp500_daily.index, dsath_sp, label='S&P 500')
plt.hlines(dsath_sp[-1], sp500_daily.index[0], sp500_daily.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
plt.plot(nasdaq_comp_daily.index, dsath_nc, alpha=0.6, label='NASDAQ Composite')
plt.plot(russel2000_daily.index, dsath_r2, alpha=0.3, label='Russel 2000')
plt.ylabel('Days since latest ATH')
plt.xlabel('Date')
plt.xlim(sp500_daily.index[-2*365], sp500_daily.index[-1])
plt.ylim(0, top_limit)
plt.gcf().autofmt_xdate()
plt.tight_layout()
# Draw an arrow from the first subplot to the second subplot
arrow = plt.Arrow(0.7, 0.25, 0.06, 0, transform=fig.transFigure, color='k', width=0.03)
fig.add_artist(arrow)
st.pyplot(fig=fig)

# Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
