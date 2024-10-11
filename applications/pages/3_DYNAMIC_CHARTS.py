import streamlit as st
from classes.ConnectToGP import ConnectToGP
import datetime
import time
import numpy as np
import plotly.express as px
from pygwalker.api.streamlit import StreamlitRenderer
import time
import gc
from psycopg2.errors import QueryCanceled

def sql_check(query: str, blacklist: list) -> bool:
    if any(x in query for x in blacklist):
        return True
    else:
        return False

@st.experimental_fragment
@st.cache_resource(ttl=1200)
def start_processing(props, sql_input) -> bool:
    st.spinner("Крутим, вертим ...")
    if sql_input != 'select * from table where {}':
        try:
            conn = ConnectToGP(props["connect"]["host"], props["connect"]["database"], statement_timeout=30000)
            df_dynamic = conn.execute_sql_pl(sql_input)
            # pyg_app = StreamlitRenderer(df_dynamic, spec=spec)
            # pyg_app.explorer()
            return df_dynamic
        except Exception as e:
            f'Wrong sql input, error {e}'
            st.stop()

def page_dynamic_charts() -> None:
    st.markdown("# Динамический BI инструмент")
    st.sidebar.header("Динамический BI инструмент")

    # open files
    props = st.session_state.props

    # dashboard
    with st.sidebar:
        clear_cache_button = st.button("Очистить кэш")
        if clear_cache_button:
            st.cache_data.clear()
            start_processing.clear()
            gc.collect()
            st.write("Cache cleared")

    with st.form("sql_input"):
        sql_input = st.text_area(
            "Введите ваш SQL запрос (не забудьте указать колонки, по которым будете строить график)",
            "select * from table where {}")

        if sql_input:
            st.markdown(f"Ваш запрос: ```{sql_input.rstrip()}```")

        sql_processing = st.form_submit_button("Start sql processing")
        if sql_processing:
            if sql_check(query=sql_input.lower(), blacklist=st.session_state.blacklist):
                st.warning("Only SELECT operations are allowed")
            else:
                df_dynamic = start_processing(props, sql_input)
                spec_input = st.text_area(
                    "Спецификация графика (опционально)",
                    "")
                pyg_app = StreamlitRenderer(df_dynamic, spec=spec_input)
                pyg_app.explorer()
                st.write("Success")


if __name__ == '__main__':

    # page options
    st.set_page_config(
        page_title="Динамический BI инструмент",
        layout="wide"
    )

    if 'st_started' in st.session_state:
        try:
            page_dynamic_charts()

        except Exception as e:
            st.warning(f"{e}")
            st.switch_page('Welcome.py')
            st.rerun()

    else:
        st.warning("Please login on welcome page")