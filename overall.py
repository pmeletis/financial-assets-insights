import time
from pathlib import Path

import pandas as pd
# import plotly.graph_objs as go
import plotly.express as px
import streamlit as st

from funclib import (INFO, _num_occurences, days_since_change,
                     get_close_data_from_dumps, batch_process)


timer_start = time.time_ns()

st.title('Insights on Financial Markets')
st.subheader('A collection of insights and analytics on the stock and cryptocurrency markets.')

daily_close_df = get_close_data_from_dumps()
assert len(daily_close_df) > 0, 'Empty daily_close dataframe.'
dsath_df = batch_process(daily_close_df)

with st.sidebar:
  st.write('Stock market indices') # :-2
  for row in INFO[['button_name', 'button_default']][:-2].itertuples():
    INFO.loc[row.Index, 'button_selection'] = st.checkbox(row.button_name, value=row.button_default)
  st.write('Cryptocurrencies') # -2:
  for row in INFO[['button_name', 'button_default']][-2:].itertuples():
    INFO.loc[row.Index, 'button_selection'] = st.checkbox(row.button_name, value=row.button_default)

columns_to_keep = INFO['filename_prefix'][INFO['button_selection']]#.to_list()
daily_close = daily_close_df[columns_to_keep]
dsath = dsath_df[columns_to_keep]
daily_close.loc[:, 'Date'] = daily_close.index
dsath.loc[:, 'Date'] = dsath_df.index

###############################################################################

st.header('Indices')

data_load_state = st.text('Creating graph...')

# melt the dataframe for Plotly Express
melted_data = daily_close.melt(id_vars='Date', var_name='index', value_name='USD')

fig = px.line(data_frame=melted_data, x='Date', y='USD', color='index', 
              # labels={'value': 'Value', 'date': 'Date', 'series': 'Series'},
              # title='Time Series Data',
              log_y=True,
)

start_year = daily_close.index.year.min()
end_year = daily_close.index.year.max()
years = list(range(1930, end_year + 1, 5))
if start_year < 1930:
  years.insert(0, start_year)
if years[-1] != end_year:
  years.append(end_year)

fig.update_layout(
    # autosize=True,
    # xaxis=dict(
    #     tickformat='%Y',  # Show year only
    #     dtick="M60",  # Tick every 60 months (5 years)
    #     tickangle=45  # Rotate labels for better readability
    # ),
    xaxis=dict(
        tickmode='array',
        tickvals=pd.to_datetime([f'{year}-01-01' for year in years]),
        ticktext=[str(year) for year in years],
        tickangle=45,  # Rotate labels for better readability
        range=[pd.to_datetime(f'{start_year}-01-01'), pd.to_datetime(f'{end_year}-12-31')],
    ),
    # yaxis=dict(
    #     minor=dict(showgrid=False)
    # ),
    # height=500  # you can adjust the height if needed
)

# fig.update_xaxes(autorange=True)

data_load_state.text('Creating graph... Done!')
st.plotly_chart(fig, use_container_width=True, theme=None)
data_load_state.empty()

############################################################################

st.header('Days since latest All Time High')

data_load_state = st.text('Creating graph...')

# Melt the dataframe for Plotly Express
melted_data = dsath.melt(id_vars='Date', var_name='index', value_name='# days')
fig = px.line(data_frame=melted_data, x='Date', y='# days', color='index', 
              # labels={'value': 'Value', 'date': 'Date', 'series': 'Series'},
              # title='Time Series Data',
              # log_y=True,
)
fig.update_yaxes(title='Days since latest ATH')

fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=pd.to_datetime([f'{year}-01-01' for year in years]),
        ticktext=[str(year) for year in years],
        tickangle=45,  # Rotate labels for better readability
        range=[pd.to_datetime(f'{start_year}-01-01'), pd.to_datetime(f'{end_year}-12-31')],
    ),
)

data_load_state.text('Creating graph... Done!')
st.plotly_chart(fig, use_container_width=True, theme=None)
data_load_state.empty()

##########################################################################################

st.header('Number of days since the latest daily change')

data_load_state = st.text('Creating graph...')

days_period = st.slider('Days period', min_value=1, max_value=30, value=1)
change = st.slider('Percentage change', min_value=-15, max_value=15, value=3, format='%d%%')

dschange = daily_close_df[columns_to_keep].apply(days_since_change, change=change, days_period=days_period)
num_occurences = daily_close_df[columns_to_keep].apply(_num_occurences, change=change).to_list()

dschange['Date'] = dschange.index
# Melt the dataframe for Plotly Express
melted_data = dschange.melt(id_vars='Date', var_name='index', value_name='# days')
title = f'Number of days since the latest at least {change}%'
fig = px.line(data_frame=melted_data, x='Date', y='# days', color='index', title=title)
fig.update_yaxes(title=f'Days since latest at least {change}% change')

fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=pd.to_datetime([f'{year}-01-01' for year in years]),
        ticktext=[str(year) for year in years],
        tickangle=45,  # Rotate labels for better readability
        range=[pd.to_datetime(f'{start_year}-01-01'), pd.to_datetime(f'{end_year}-12-31')],
    ),
)

data_load_state.text('Creating graph... Done!')
st.plotly_chart(fig, use_container_width=True, theme=None)
data_load_state.empty()
st.text(f'Num occurences per index: {num_occurences}.')

# horizontal separator
st.markdown("---")

st.write()
outro_str = """
© 2024-2025, P. Meletis.

You can find the source for this website at https://github.com/pmeletis/financial-assets-insights.
"""
st.write(outro_str)
st.write(f'Page created in {(time.time_ns() - timer_start) / 1_000_000_000:.1f} sec.')
