import streamlit as st

st.subheader('Calculating index ratios')
st.write('Stocks and stock market indices are typically '
         'denominated in specific currencies, whose values are influenced by factors such as '
         'inflation, interest rates, and economic policies. Using ratios of indices instead of the '
         'indices themselves is crucial for *evaluating the relative performance of stocks* and '
         'helps *adjust for the impact of currency fluctuations*, providing a clearer comparison '
         'of their underlying market trends.')
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
