from datetime import date
from functools import partial
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from funclib import (days_since_ath, download_and_save_data,
                     get_latest_close_data)

# import pandas as pd
# import yfinance as yf
# import mpld3
# import streamlit.components.v1 as components

DIRPATH_DATASET = Path.absolute(Path('.')) / 'datasets'


st.title('Insights on Financial Markets')

data_load_state = st.text('Loading data...')

st.header('Indices')

daily_close = get_latest_close_data(DIRPATH_DATASET)

data_load_state.text('Loading data... done!')

data_load_state.text('Creating graphs...')

col1, col2, col3 = st.columns(3)
sp_check = col1.checkbox('S&P500', value=True)
nc_check = col2.checkbox('NASDAQ Comp', value=True)
r2_check = col3.checkbox('RUSSEL2000', value=True)

colors = dict(zip(daily_close.columns, plt.cm.tab10.colors))
fig = plt.figure(figsize=(14, 7), dpi=300)
if sp_check:
  plt.plot(daily_close['S&P500'], color=colors['S&P500'], label='S&P500')
  plt.hlines(daily_close['S&P500'].iloc[-1], daily_close.index[0], daily_close.index[-1], colors=colors['S&P500'], linestyles='--', alpha=0.3, zorder=-1)
if nc_check:
  plt.plot(daily_close['NASDAQ Comp'], color=colors['NASDAQ Comp'], label='NASDAQ Comp')
  plt.hlines(daily_close['NASDAQ Comp'].iloc[-1], daily_close.index[0], daily_close.index[-1], colors=colors['NASDAQ Comp'], linestyles='--', alpha=0.3, zorder=-1)
if r2_check:
  plt.plot(daily_close['RUSSEL2000'], color=colors['RUSSEL2000'], label='RUSSEL2000')
  plt.hlines(daily_close['RUSSEL2000'].iloc[-1], daily_close.index[0], daily_close.index[-1], colors=colors['RUSSEL2000'], linestyles='--', alpha=0.3, zorder=-1)
plt.yscale('log')
plt.xlabel('Date')
plt.xlim(left=daily_close.index[0], right=daily_close.index[-1])
plt.tick_params(axis='y', which='both', right=True, labelright=True)
plt.tight_layout()
plt.legend()
st.pyplot(fig=fig)


dsath =  daily_close.apply(days_since_ath)
dsath_sp = dsath['S&P500']
dsath_nc = dsath['NASDAQ Comp']
dsath_r2 = dsath['RUSSEL2000']
top_limit = max(*dsath_sp[-2*365:], *dsath_nc[-2*365:], *dsath_r2[-2*365:])

fig, _ = plt.subplots(ncols=2, figsize=(12,5), width_ratios=(3, 1))
plt.subplot(1, 2, 1)
plt.plot(dsath['S&P500'], label='S&P500')
plt.hlines(dsath_sp.iloc[-1], dsath_sp.index[0], dsath_sp.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
plt.plot(dsath_nc, alpha=0.6, label='NASDAQ Composite')
plt.plot(dsath_r2, alpha=0.3, label='Russel 2000')
plt.ylabel('Days since latest ATH')
plt.xlabel('Date')
plt.legend()

# rect = patches.Rectangle((plt.xlim()[1]-100, 0), 40, top_limit, linewidth=1, edgecolor='r', facecolor='none')
# plt.gca().add_patch(rect)
plt.subplot(1, 2, 2)
plt.plot(dsath['S&P500'], label='S&P500')
plt.hlines(dsath_sp.iloc[-1], dsath_sp.index[0], dsath_sp.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
plt.plot(dsath_nc, alpha=0.6, label='NASDAQ Composite')
plt.plot(dsath_r2, alpha=0.3, label='Russel 2000')
plt.ylabel('Days since latest ATH')
plt.xlabel('Date')
plt.xlim(dsath_sp.index[-2*365], dsath_sp.index[-1])
plt.ylim(0, top_limit)
plt.gcf().autofmt_xdate()
plt.tight_layout()
# Draw an arrow from the first subplot to the second subplot
arrow = plt.Arrow(0.7, 0.25, 0.06, 0, transform=fig.transFigure, color='k', width=0.03)
fig.add_artist(arrow)
st.pyplot(fig=fig)

data_load_state.text('Creating graphs... done!')

# Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
