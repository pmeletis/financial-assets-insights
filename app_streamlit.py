import streamlit as st


st.set_page_config(
    page_title="Financial Markets insights",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

pages = {
    "Stock markets": [
        st.Page("index_ratios.py", title="Index ratios"),
    ],
    "Overall": [
        st.Page("overall.py", title="Overall"),
    ],
}

pg = st.navigation(pages)
pg.run()
