import time

import altair as alt
import streamlit as st

from funclib import get_ratios_df

alt.data_transformers.enable('vegafusion')

timer_start = time.time_ns()

st.title('Insights on Financial Markets')
st.subheader('A collection of insights and analytics on the stock and cryptocurrency markets.')

st.write('SPX: S&P 500 Index. A market-capitalization-weighted index of the 500 largest US companies.')
st.write('SPX equal weight: S&P 500 Equal Weight Index. An equal-weighted version of the S&P 500 Index.')
st.write('Wilshire 5000 Total Market Index: all American stocks. A market-capitalization-weighted index '
         'with around 3.5k stocks, including the majority of common stocks and REITs traded through '
         'NYSE, NASDAQ, or AMEX, and excluding limited partnerships and ADRs.')

ratios_df = get_ratios_df(subsample_step=4, append_date_column=True)

# generate chart
tableau_colors = ['#4C78A8', '#F58518']
base = alt.Chart(ratios_df).encode(x=alt.X('date:T', title='date'))
# add y1 and y2 charts
y1_schema = alt.Y('spx/ftw5000:Q',
                  axis=alt.Axis(title='SPX / Wilshire 5000', titleColor=tableau_colors[0]),
                  scale=alt.Scale(zero=False))
y1_tooltips = [alt.Tooltip('date:T', title='date'),
               alt.Tooltip('spx/ftw5000:Q', title='SPX / Wilshire 5000', format='.3f')]
y1_chart = base.mark_line(color=tableau_colors[0]).encode(y=y1_schema, tooltip=y1_tooltips).interactive()
y2_schema = alt.Y('spx/spxew:Q',
                  axis=alt.Axis(title='SPX / SPX Equal Weight', titleColor=tableau_colors[1]),
                  scale=alt.Scale(zero=False))
y2_tooltips = [alt.Tooltip('date:T', title='date'),
               alt.Tooltip('spx/spxew:Q', title='SPX / SPX Equal Weight', format='.3f')]
y2_chart = base.mark_line(color=tableau_colors[1]).encode(y=y2_schema, tooltip=y2_tooltips).interactive()
# Overlay the charts
twin_axes_chart = alt.layer(y1_chart, y2_chart).resolve_scale(
    y='independent').interactive()

# display the chart
st.altair_chart(twin_axes_chart, use_container_width=True)

# horizontal separator
st.markdown("---")

st.write()
outro_str = """
© 2024-2025, P. Meletis.

You can find the source for this website at https://github.com/pmeletis/financial-assets-insights.
"""
st.write(outro_str)
st.write(f'Page created in {(time.time_ns() - timer_start) / 1_000_000_000:.1f} sec.')
