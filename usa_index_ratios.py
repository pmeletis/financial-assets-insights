import time

import altair as alt
import pandas as pd
import streamlit as st

from description_strings import (description_ftw5000, description_ixic,
                                 description_ndx, description_spx,
                                 description_spxew, description_usgdp,
                                 outro_string)
from funclib import generate_twin_chart, get_ratios_df

alt.data_transformers.enable('vegafusion')

timer_start = time.time_ns()

st.title('Comparing economy and market cap indicators')
st.write(
    'This page presents key index ratios that I use for discovering dynamics and (macro-) '
    'economic trends of stock markets. Using ratios of indices instead of the '
    'indices themselves is crucial for *evaluating the relative performance of stocks* and '
    'helps *adjust for the impact of currency fluctuations*, providing a clearer comparison '
    'of their underlying market trends.')

ratios_df = get_ratios_df(symbol_source='20241203', subsample_step=4, append_date_column=True)

# Chart 1 #########################################################################################
st.header('Economic indicators - Market cap')
st.write('Comparing the US GDP with the S&P 500 and total market capitalization (Wilshire 5000).')

with st.expander('Data info', expanded=False, icon=':material/info:'):
  st.write(description_usgdp)
  st.write(description_spx)
  st.write(description_ftw5000)

twin_axes_chart = generate_twin_chart(ratios_df,
                                      'spx/usgdp', 'S&P 500   /   GDP real',
                                      'ftw5000/usgdp', 'Total market   /   GDP real')
# theme=None is needed because streamlit doesn't handle vegafusion for now
st.altair_chart(twin_axes_chart, use_container_width=True, theme=None)

# Chart 2 ########################################################################################
st.header('S&P 500 ratios')
st.write('Comparing the market-cap-weighted 500 largest US companies (S&P 500) with the total US '
         'stock market (Wilshire 5000) and the equally-weighted S&P 500 index.')

with st.expander('Data info', expanded=False, icon=':material/info:'):
  st.write(description_spx)
  st.write(description_ftw5000)
  st.write(description_spxew)

st.write('')  # leave an empty space

twin_axes_chart = generate_twin_chart(ratios_df,
                                      'spx/ftw5000', 'S&P 500   /   Total market',
                                      'spx/spxew', 'S&P 500   /   S&P 500 EW')
st.altair_chart(twin_axes_chart, use_container_width=True)

# Chart 3 #########################################################################################
st.header('NASDAQ 100 ratios')
st.write('Comparing the market-cap-weighted 100 largest non-financial companies listed on NASDAQ '
         '(NASDAQ 100) with the S&P 500 and all common stocks listed on NASDAQ (NASDAQ Composite).')
st.markdown('> The NASDAQ 100 significantly outperforms the S&P 500 and delivers twice the '
            'returns of the NASDAQ Composite.')
st.markdown('> When trading the ratios, the NASDAQ 100 - NASDAQ Composite pair has smaller drawdowns.')

with st.expander('Data info', expanded=False, icon=':material/info:'):
  st.write(description_ndx)
  st.write(description_spx)
  st.write(description_ixic)

st.write('')  # leave an empty space

# generate chart
twin_axes_chart = generate_twin_chart(ratios_df,
                                      'ndx/spx', 'NASDAQ 100   /   S&P 500',
                                      'ndx/ixic', 'NASDAQ 100   /   NASDAQ Composite')
st.altair_chart(twin_axes_chart, use_container_width=True)

st.divider()

# Outro ###########################################################################################
st.write('')
st.write(outro_string)
st.write(f'Page created in {(time.time_ns() - timer_start) / 1_000_000_000:.1f} sec.')
