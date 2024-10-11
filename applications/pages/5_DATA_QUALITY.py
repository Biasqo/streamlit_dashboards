import streamlit as st
from classes.ConnectToGP import ConnectToGP
from classes.FileOpener import FileOpener
import datetime
import time
import plotly.express as px
import itertools


@st.cache_resource(ttl=3600 * 8)
def get_data(props, _func, path, date_dq) -> "pd.DataFrame":
    conn = ConnectToGP(props["connect"]["host"], props["connect"]["database"], statement_timeout=30000)
    return conn.execute_sql_pl(_func(path).format(date_dq[0], date_dq[1]))


def df_page_dq() -> None:
    st.markdown("# Простой инструмент DQ")
    st.sidebar.header("Простой инструмент DQ")

    # get file opener
    file_opener = FileOpener()

    # open files and connect
    props = st.session_state.props

    # datetime
    date_today = datetime.datetime.now()
    prev_year = date_today.year - 1
    jan_1 = datetime.date(prev_year, 1, 1)
    dec_31 = datetime.date(date_today.year, 12, 31)

    date_dq = st.date_input("Application date", (datetime.date(date_today.year, 1, 1), dec_31), jan_1, dec_31)
    if len(date_dq) < 2:
        date_dq = date_dq + (dec_31,)

    # columns
    col1, col2 = st.columns(2)

    with st.sidebar:
        clear_cache_button = st.button("Обновить и очистить кэш")
        if clear_cache_button:
            st.cache_data.clear()
            get_data.clear()
            st.write("Cache cleared")

    df_dpta_rc_avg = get_data(props, file_opener.sql_open, "sql_queries/dq/check_dpta_rc_avg.sql", date_dq)
    df_dlrcap_rc_cnt = get_data(props, file_opener.sql_open, "sql_queries/dq/check_dlrcap_rc_cnt.sql", date_dq)
    df_trc_cv_ucl_cnt = get_data(props, file_opener.sql_open, "sql_queries/dq/check_trc_cv_ucl_cnt.sql",
                                 date_dq)
    df_appr_issued_cnt = get_data(props, file_opener.sql_open, "sql_queries/dq/check_appr_issued_cnt.sql",
                                  date_dq)
    df_recalc = get_data(props, file_opener.sql_open, "sql_queries/dq/check_recalc_cnt.sql",
                                  date_dq)
    df_default = get_data(props, file_opener.sql_open, "sql_queries/dq/check_portfolio_table.sql",
                                  date_dq)

    # figs
    fig_dpta_rc_avg = px.line(df_dpta_rc_avg, x='appl_dt', y=['avg_risk_cost', 'avg_risk_cost_issued']
                              , title='DQ dds_pil_tsmr_appls (average risk cost)')
    fig_dlrcap_rc_cnt = px.line(df_dlrcap_rc_cnt, x='timestampcolumn', y='count_risk_cost',
                                title='DQ dds_ll_rr_cp_attrs_pil (count zero risk cost logs)')
    fig_trc_cv_ucl_cnt = px.line(df_trc_cv_ucl_cnt, x='cv_ucl_date', y=['rq_count', 'rs_count'],
                                 title='DQ tech_log_ezht_codes (average CV_UCL rq and rs day by day)')
    fig_appr_issued_cnt = px.line(df_appr_issued_cnt, x='appl_dt', y=['appl_cnt', 'issued_cnt'],
                                  title='DQ v_05_13_t_applret_param (applret_param appl cnt)')
    fig_df_recalc = px.line(df_recalc, x='appl_dt', y=['sum_rc', 'cnt_appls'],
                                  title='DQ dm_appls_metrics_recalc (recalc count of appls and rc)')
    fig_df_default = px.line(df_default, x='appl_dt', y='cnt_appls',
                                  title='DQ dds_pil_default (cnt appls)')

    with col1:
        st.plotly_chart(fig_dpta_rc_avg)
        st.plotly_chart(fig_trc_cv_ucl_cnt)
        st.plotly_chart(fig_df_recalc)

    with col2:
        st.plotly_chart(fig_dlrcap_rc_cnt)
        st.plotly_chart(fig_appr_issued_cnt)
        st.plotly_chart(fig_df_default)


if __name__ == '__main__':

    # page options
    st.set_page_config(
        page_title="Basic Data Quality",
        layout="wide"
    )

    if 'st_started' in st.session_state:
        try:
            df_page_dq()

        except Exception as e:
            st.warning(f"{e}")
            st.switch_page('Welcome.py')
            st.rerun()

    else:
        st.warning("Please login on welcome page")
