import streamlit

html = """
  <style>


    /* Remove horizontal scroll */
    .element-container {
      width: auto !important;
    }

    .fullScreenFrame > div {
      width: auto !important;
    }
  </style>
"""
st.markdown(html, unsafe_allow_html=True)
