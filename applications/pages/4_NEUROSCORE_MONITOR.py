import streamlit as st
from classes.ConnectToGP import ConnectToGP
import datetime
import time
import pandas as pd
import plotly.express as px
import datetime
import time


def neuroscore_monitor() -> None:
    st.markdown("# Мониторинг нейроскоров")
    st.sidebar.header("Мониторинг нейроскоров")

    # open files
    props = st.session_state.props

    # datetime
    date_today = datetime.datetime.now()
    jan_1 = datetime.date(date_today.year, 1, 1)
    dec_31 = datetime.date(date_today.year, 12, 31)

    # dashboard
    date_nm = st.date_input("Report date", (datetime.date(date_today.year, 1, 1), dec_31), jan_1, dec_31)
    if len(date_nm) < 2:
        date_nm = date_nm + (dec_31,)

    # columns
    col1, col2 = st.columns(2)

    # get new connection
    conn = ConnectToGP(props["connect"]["host"], props["connect"]["database"], statement_timeout=30000)

    df_cnt_ct1002 = conn.execute_sql_pd(
        f"select * from rrb_pil.mv_streamlit_monitor_cnt_ct1002 "
        f"where report_date_part::date between \'{date_nm[0]}\' and \'{date_nm[1]}\' "
        f"order by report_date_part asc")
    df_avg = conn.execute_sql_pd(
        f"select * from rrb_pil.mv_streamlit_neuroscore_avg "
        f"where report_date_part::date between \'{date_nm[0]}\' and \'{date_nm[1]}\' "
        f"order by report_date_part asc")
    df_cnt_ct4001 = conn.execute_sql_pd(
        f"select * from rrb_pil.mv_streamlit_monitor_cnt_ct4001 "
        f"where report_date_part::date between \'{date_nm[0]}\' and \'{date_nm[1]}\' "
        f"order by report_date_part asc")

    # figs
    fig_cnt_ct1002 = px.bar(df_cnt_ct1002, x="report_date_part", y="count_bundle", color="bucket_ct1002"
                            , color_discrete_sequence=['indigo', 'darkviolet', 'darkorchid', 'mediumorchid',
                                                       'orchid', 'violet', 'plum']
                            , title="Бакеты скоров CT1002")
    fig_cnt_ct4001 = px.bar(df_cnt_ct4001, x="report_date_part", y="count_bundle", color="bucket_ct4001"
                            , color_discrete_sequence=['darkgreen', 'green', 'forestgreen', 'mediumseagreen',
                                                       'lawngreen', 'greenyellow', 'yellow']
                            , title="Бакеты скоров CT4001")
    fig_nulls_cnt = px.line(df_avg, x='report_date_part',
                            y=['nulls_ct4001', 'nulls_ct1002', 'count_rows'],
                            color_discrete_sequence=["orange", "orangered", "yellow"],
                            title='CT1002 и CT4001 количество')

    fig_avg = px.line(df_avg, x='report_date_part',
                      y=['avg_ct4001', 'avg_ct1002'],
                      title='CT1002 и CT4001 средние значения')

    with col1:
        st.plotly_chart(fig_cnt_ct1002)
        st.plotly_chart(fig_avg)

    with col2:
        st.plotly_chart(fig_cnt_ct4001)
        st.plotly_chart(fig_nulls_cnt)


if __name__ == '__main__':

    # page options
    st.set_page_config(
        page_title="Мониторинг нейроскоров",
        layout="wide"
    )

    if 'st_started' in st.session_state:
        try:
            neuroscore_monitor()

        except Exception as e:
            st.warning(f"{e}")
            st.switch_page('Welcome.py')
            st.rerun()

    else:
        st.warning("Please login on welcome page")
