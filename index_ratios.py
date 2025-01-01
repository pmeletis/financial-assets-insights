import time

import altair as alt
import pandas as pd
import streamlit as st

from description_strings import (description_ftw5000, description_ixic,
                                 description_ndx, description_spx,
                                 description_spxew, outro_string)
from funclib import get_ratios_df

alt.data_transformers.enable('vegafusion')

timer_start = time.time_ns()

def generate_twin_chart(data: pd.DataFrame, y1_col: str, y1_title: str, y2_col: str, y2_title: str
                        ) -> alt.Chart:
  tableau_colors = ['#4C78A8', '#F58518']
  base = alt.Chart(data).encode(x=alt.X('date:T', title='date'))
  # add y1 and y2 charts
  y1_schema = alt.Y(y1_col + ':Q',
                    axis=alt.Axis(title=y1_title, titleColor=tableau_colors[0]),
                    scale=alt.Scale(zero=False))
  y1_tooltips = [alt.Tooltip('date:T', title='date'),
                 alt.Tooltip(y1_col + ':Q', title=y1_title, format='.3f')]
  y1_chart = base.mark_line(color=tableau_colors[0]).encode(y=y1_schema, tooltip=y1_tooltips).interactive()
  y2_schema = alt.Y(y2_col + ':Q',
                    axis=alt.Axis(title=y2_title, titleColor=tableau_colors[1]),
                    scale=alt.Scale(zero=False))
  y2_tooltips = [alt.Tooltip('date:T', title='date'),
                 alt.Tooltip(y2_col + ':Q', title=y2_title, format='.3f')]
  y2_chart = base.mark_line(color=tableau_colors[1]).encode(y=y2_schema, tooltip=y2_tooltips).interactive()
  # Overlay the charts
  twin_axes_chart = alt.layer(y1_chart, y2_chart).resolve_scale(y='independent').interactive()
  return twin_axes_chart

st.title('Comparing various stock market indices')
st.write(
    'This page presents key index ratios that I use for discovering dynamics and (macro-) '
    'economic trends of stock markets. Stocks and stock market indices are typically '
    'denominated in specific currencies, whose values are influenced by factors such as '
    'inflation, interest rates, and economic policies. Using ratios of indices instead of the '
    'indices themselves is crucial for *evaluating the relative performance of stocks* and '
    'helps *adjust for the impact of currency fluctuations*, providing a clearer comparison '
    'of their underlying market trends.')

st.subheader('Calculating index ratios')
st.write('The index ratio is calculated as the ratio of two stock baskets, denominated in their '
          'currencies. The formula is:')
st.write('$\\text{Index ratio} = \\frac{\\frac{\\text{stock basket}_1}{\\text{currency}_1}}'
         '                             {\\frac{\\text{stock basket}_2}{\\text{currency}_2}}'
         '                     = \\frac{\\text{stock basket}_1}{\\text{stock basket}_2} \\times '
         '                       \\frac{\\text{currency}_2}{\\text{currency}_1}$')
st.write('When the denominating currencies are the same the ratio simplifies to:')
st.write('$\\text{Index ratio} = \\frac{\\text{stock basket}_1}{\\text{stock basket}_2}$')
st.write('When the ratio increases, the first stock basket is outperforming the second, and vice '
         'versa when the ratio decreases.')
st.write('When the denominating currencies are different, then we need to multiply with the '
         'forex ratio.')

ratios_df = get_ratios_df(symbol_source='20241203', subsample_step=4, append_date_column=True)

# Chart 1 ########################################################################################
st.header('USA stock market: S&P 500 ratios')
st.write('The S&P 500 index represents the 500 largest US companies. Here we compare it with '
         'the total US stock market (Wilshire 5000) and the S&P 500 Equal Weight index.')

with st.expander('Data info', expanded=False, icon=':material/info:'):
  st.write(description_spx)
  st.write(description_ftw5000)
  st.write(description_spxew)

st.write('')  # leave an empty space

twin_axes_chart = generate_twin_chart(ratios_df,
                                      'spx/ftw5000', 'S&P 500  /  Wilshire 5000',
                                      'spx/spxew', 'S&P 500  /  S&P 500 Equal Weight')
st.altair_chart(twin_axes_chart, use_container_width=True)


# Chart 2 #########################################################################################
st.header('USA stock market: NASDAQ 100 ratios')
st.write('The NASDAQ 100 index represents the 100 largest non-financial companies listed on '
         'NASDAQ. Here we compare it with the S&P 500, which contains a broader selection of '
         'companies, and the NASDAQ Composite index, which includes all common stocks listed on'
         'NASDAQ.')

with st.expander('Data info', expanded=False, icon=':material/info:'):
  st.write(description_ndx)
  st.write(description_spx)
  st.write(description_ixic)

st.write('')  # leave an empty space

# generate chart
twin_axes_chart = generate_twin_chart(ratios_df,
                                      'ndx/spx', 'NASDAQ 100  /  S&P 500',
                                      'ndx/ixic', 'NASDAQ 100  /  NASDAQ Composite')
st.altair_chart(twin_axes_chart, use_container_width=True)

st.divider()

# Outro ###########################################################################################
st.write('')
st.write(outro_string)
st.write(f'Page created in {(time.time_ns() - timer_start) / 1_000_000_000:.1f} sec.')
