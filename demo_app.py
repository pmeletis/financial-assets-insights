from pathlib import Path

import pandas as pd
# import plotly.graph_objs as go
import plotly.express as px
import streamlit as st

from funclib import days_since_ath, get_close_data_from_dumps

# DIRPATH_DATASET = Path.absolute(Path('.')) / 'datasets'


st.title('Insights on Financial Markets')

intro_str = """A collection of insights and analytics on the stock and cryptocurrency markets.

You can find the source for this website at https://github.com/pmeletis/financial-assets-insights.
"""
st.write(intro_str)

daily_close_df = get_close_data_from_dumps()

###############################################################################

st.header('Indices')

data_load_state = st.text('Creating graph...')

daily_close = daily_close_df.copy()
daily_close['Date'] = daily_close.index
# Melt the dataframe for Plotly Express
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

dsath = daily_close_df.copy()
dsath = dsath.apply(days_since_ath)

dsath['Date'] = dsath.index
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

# dsath_sp = dsath['S&P500']
# dsath_nc = dsath['NASDAQ Comp']
# dsath_r2 = dsath['RUSSEL2000']
# dsath_btc = dsath['BTCUSD']
# fig, _ = plt.subplots(ncols=2, figsize=(12,5), width_ratios=(3, 1))
# plt.subplot(1, 2, 1)
# plt.plot(dsath['S&P500'], label='S&P500')
# plt.hlines(dsath_sp.iloc[-1], dsath_sp.index[0], dsath_sp.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
# plt.plot(dsath_nc, alpha=0.7, label='NASDAQ Composite')
# plt.plot(dsath_r2, alpha=0.5, label='Russel 2000')
# plt.plot(dsath_btc, alpha=0.5, label='BTC')
# plt.gca().xaxis.set_major_locator(YearLocator(base=5))
# plt.ylabel('Days since latest ATH')
# plt.xlabel('Date')
# plt.legend()


# col1, col2, col3 = st.columns(3)
# sp_check = col1.checkbox('S&P500', value=True)
# nc_check = col2.checkbox('NASDAQ Comp', value=True)
# r2_check = col3.checkbox('RUSSEL2000', value=True)

# fig = go.Figure()

# if sp_check:
#     fig.add_trace(go.Scatter(x=data['date'], y=data['series1'], mode='lines', name='Series 1'))
# if show_series2:
#     fig.add_trace(go.Scatter(x=data['date'], y=data['series2'], mode='lines', name='Series 2'))
# if show_series3:
#     fig.add_trace(go.Scatter(x=data['date'], y=data['series3'], mode='lines', name='Series 3'))

# Update layout
# fig.update_layout(title='Time Series Data', xaxis_title='Date', yaxis_title='Value')

# Display the plot in Streamlit
# st.plotly_chart(fig)

# colors = dict(zip(daily_close.columns, plt.cm.tab10.colors))
# fig = plt.figure(figsize=(14, 7), dpi=300)
# if sp_check:
#   plt.plot(daily_close['S&P500'], color=colors['S&P500'], label='S&P500')
#   plt.hlines(daily_close['S&P500'].iloc[-1], daily_close.index[0], daily_close.index[-1], colors=colors['S&P500'], linestyles='--', alpha=0.3, zorder=-1)
# if nc_check:
#   plt.plot(daily_close['NASDAQ Comp'], color=colors['NASDAQ Comp'], label='NASDAQ Comp')
#   plt.hlines(daily_close['NASDAQ Comp'].iloc[-1], daily_close.index[0], daily_close.index[-1], colors=colors['NASDAQ Comp'], linestyles='--', alpha=0.3, zorder=-1)
# if r2_check:
#   plt.plot(daily_close['RUSSEL2000'], color=colors['RUSSEL2000'], label='RUSSEL2000')
#   plt.hlines(daily_close['RUSSEL2000'].iloc[-1], daily_close.index[0], daily_close.index[-1], colors=colors['RUSSEL2000'], linestyles='--', alpha=0.3, zorder=-1)
# plt.yscale('log')
# plt.xlabel('Date')
# plt.xlim(left=daily_close.index[0], right=daily_close.index[-1])
# plt.tick_params(axis='y', which='both', right=True, labelright=True)
# plt.tight_layout()
# plt.legend()
# st.pyplot(fig=fig)


# dsath =  daily_close.apply(days_since_ath)
# dsath_sp = dsath['S&P500']
# dsath_nc = dsath['NASDAQ Comp']
# dsath_r2 = dsath['RUSSEL2000']
# top_limit = max(*dsath_sp[-2*365:], *dsath_nc[-2*365:], *dsath_r2[-2*365:])

# fig, _ = plt.subplots(ncols=2, figsize=(12,5), width_ratios=(3, 1))
# plt.subplot(1, 2, 1)
# plt.plot(dsath['S&P500'], label='S&P500')
# plt.hlines(dsath_sp.iloc[-1], dsath_sp.index[0], dsath_sp.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
# plt.plot(dsath_nc, alpha=0.6, label='NASDAQ Composite')
# plt.plot(dsath_r2, alpha=0.3, label='Russel 2000')
# plt.ylabel('Days since latest ATH')
# plt.xlabel('Date')
# plt.legend()

# # rect = patches.Rectangle((plt.xlim()[1]-100, 0), 40, top_limit, linewidth=1, edgecolor='r', facecolor='none')
# # plt.gca().add_patch(rect)
# plt.subplot(1, 2, 2)
# plt.plot(dsath['S&P500'], label='S&P500')
# plt.hlines(dsath_sp.iloc[-1], dsath_sp.index[0], dsath_sp.index[-1], linestyles='--', alpha=0.3, label='S&P 500 days since ATH')
# plt.plot(dsath_nc, alpha=0.6, label='NASDAQ Composite')
# plt.plot(dsath_r2, alpha=0.3, label='Russel 2000')
# plt.ylabel('Days since latest ATH')
# plt.xlabel('Date')
# plt.xlim(dsath_sp.index[-2*365], dsath_sp.index[-1])
# plt.ylim(0, top_limit)
# plt.gcf().autofmt_xdate()
# plt.tight_layout()
# # Draw an arrow from the first subplot to the second subplot
# arrow = plt.Arrow(0.7, 0.25, 0.06, 0, transform=fig.transFigure, color='k', width=0.03)
# fig.add_artist(arrow)
# st.pyplot(fig=fig)


# Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
