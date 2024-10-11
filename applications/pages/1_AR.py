import streamlit as st
from classes.ConnectToGP import ConnectToGP
from classes.QueryMaker import QueryMaker
import datetime
import time
import plotly.express as px

def page_ar() -> None:
    st.markdown("# Уровень одобрения ПК.ПРМ")
    st.sidebar.header("Уровень одобрения ПК.ПРМ")

    # columns
    col1, col2 = st.columns(2)

    # open files and connect
    props = st.session_state.props

    # connect
    conn = ConnectToGP(props["connect"]["host"], props["connect"]["database"], statement_timeout=30000)

    # filters
    filters = st.session_state.filters

    # filter options
    client_groups = filters["client_groups"]
    products = filters["products"]
    process_codes = filters["process_codes"]
    appl_sales_channel = filters["appl_sales_channel"]

    # datetime
    date_today = datetime.datetime.now()
    prev_year = date_today.year - 1
    jan_1 = datetime.date(prev_year, 1, 1)
    dec_31 = datetime.date(date_today.year, 12, 31)

    # col1
    with col1:
        date_ar = st.date_input("Application date", (datetime.date(date_today.year, 1, 1), dec_31), jan_1, dec_31)
        if len(date_ar) < 2:
            date_ar = date_ar + (dec_31,)

        options_client = st.multiselect("Категория клиента", client_groups)
        if not options_client:
            options_client = client_groups

        options_appl_sales_channel = st.multiselect("Канал продажи", appl_sales_channel)
        if not options_appl_sales_channel:
            options_appl_sales_channel = appl_sales_channel

    # col2
    with col2:
        options_oneclick_flg = st.multiselect("Флаг oneclick", ["0", "1"])
        if not options_oneclick_flg:
            options_oneclick_flg = ["0", "1"]

        options_products = st.multiselect("Продукт", products)
        if not options_products:
            options_products = products

        options_process_codes = st.multiselect("Процесс", process_codes)
        if not options_process_codes:
            options_process_codes = process_codes

    options_client = "','".join(options_client)
    options_products = "','".join(options_products)
    options_process_codes = "$$,$$".join(options_process_codes)
    options_appl_sales_channel = "','".join(options_appl_sales_channel)
    options_oneclick_flg = ",".join(options_oneclick_flg)

    # query
    # TODO: change filters to pandas dataframe, not to data from database to use cache decorator
    ar = QueryMaker()
    ar.add_select("""
                case
                    when sum(reviewed_amt) > 0
                    then round(100 * sum(approved_amt)/sum(reviewed_amt):: decimal, 2)
                    end as ar_rub,
                case
                    when sum(reviewed_dedub_amt) > 0
                    then round(100 * sum(approved_dedub_amt)/sum(reviewed_dedub_amt):: decimal, 2)
                    end as ar_dedub_rub,
                case 
                    when sum(reviewed_cnt) > 0 
                    then round(100 * sum(approved_cnt)/sum(reviewed_cnt):: decimal, 2) 
                    end as ar,
                case 
                    when sum(reviewed_dedub_cnt) > 0 
                    then round(100 * sum(approved_dedub_cnt)/sum(reviewed_dedub_cnt):: decimal, 2) 
                    end as ar_dedub,
                appl_dt
                """) \
        .add_table('rrb.dm_ll_appl_cp') \
        .add_where(
        f'product_type_id = \'1\' and appl_dt::date between date \'{date_ar[0]}\' and \'{date_ar[1]}\' '
        f'and appl_cust_group_code in (\'{options_client}\') and appl_product_lvl_2_text in (\'{options_products}\')'
        f'and cp_process_code_text in ($${options_process_codes}$$) and '
        f'appl_sales_channel_lvl_1_text in (\'{options_appl_sales_channel}\') and '
        f'oneclick_flg in ({options_oneclick_flg})') \
        .add_group_by(f'appl_dt')

    df = conn.execute_sql_pd(ar.query)
    # df = execute_query(conn, ar.query)
    df = df.sort_values('appl_dt')

    # show plot
    fig_ar_rub = px.line(df, x='appl_dt', y=['ar_rub', 'ar_dedub_rub'], title='AR в рублях')
    fig_ar = px.line(df, x='appl_dt', y=['ar', 'ar_dedub'], title='AR в штуках')

    with col1:
        st.plotly_chart(fig_ar)

    with col2:
        st.plotly_chart(fig_ar_rub)


if __name__ == '__main__':

    # page options
    st.set_page_config(
        page_title="Уровень одобрения ПК.ПРМ",
        layout="wide"
    )

    if 'st_started' in st.session_state:
        try:
            page_ar()

        except Exception as e:
            st.warning(f"{e}")
            st.switch_page('Welcome.py')
            st.rerun()

    else:
        st.warning("Please login on welcome page")