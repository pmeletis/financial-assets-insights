import streamlit as st
import pandas as pd
import numpy as np

st.title('Uber pickups in NYC')

st.subheader('Number of pickups by hour')

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
