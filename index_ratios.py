import time

import altair as alt
import pandas as pd
import streamlit as st

from description_strings import (description_ftw5000, description_ixic,
                                 description_ndx, description_spx,
                                 description_spxew)
from funclib import get_outro_string, get_ratios_df

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

st.title('Insights on Financial Markets')
st.subheader('A collection of insights and analytics on the stock and cryptocurrency markets.')

ratios_df = get_ratios_df(symbol_source='20241203', subsample_step=4, append_date_column=True)

# Chart 1 ########################################################################################
with st.expander('Symbols description', expanded=False, icon=':material/info:'):
  st.write(description_spx)
  st.write(description_ftw5000)
  st.write(description_spxew)

st.write('')  # leave an empty space

twin_axes_chart = generate_twin_chart(ratios_df,
                                      'spx/ftw5000', 'SPX  /  Wilshire 5000',
                                      'spx/spxew', 'SPX  /  SPX Equal Weight')
st.altair_chart(twin_axes_chart, use_container_width=True)

st.divider()

## Chart 2 ########################################################################################
with st.expander('Symbols description', expanded=False, icon=':material/info:'):
  st.write(description_ndx)
  st.write(description_spx)
  st.write(description_ixic)

st.write('')  # leave an empty space

# generate chart
twin_axes_chart = generate_twin_chart(ratios_df, 'ndx/spx', 'NASDAQ 100  /  S&P 500', 'ndx/ixic', 'NASDAQ 100  /  NASDAQ Composite')
st.altair_chart(twin_axes_chart, use_container_width=True)

st.divider()

# Outro ###########################################################################################
st.write('')
st.write(get_outro_string())
st.write(f'Page created in {(time.time_ns() - timer_start) / 1_000_000_000:.1f} sec.')
