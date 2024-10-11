import streamlit as st
from classes.ConnectToGP import ConnectToGP
from classes.QueryMaker import QueryMaker
import datetime
import time
import plotly.express as px
import itertools

def page_ar_reg() -> None:
    st.markdown("# Уровень одобрения ПК.ПРМ по Регионам")
    st.sidebar.header("Уровень одобрения ПК.ПРМ по Регионам")

    # columns
    col1, col2 = st.columns(2)

    # open files and connect
    props = st.session_state.props

    # connect
    conn = ConnectToGP(props["connect"]["host"], props["connect"]["database"], statement_timeout=30000)

    # filters
    filters = st.session_state.filters

    # date
    date_ar = [
        datetime.datetime.today().replace(day=1).replace(year=datetime.datetime.now().year - 1).strftime("%Y-%m-%d")
        , (datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m-%d")]

    # filter options
    client_groups = filters["client_groups_dict"]
    products = filters["products"]
    region_codes = filters["region_code"]
    appl_sales_channel = filters["sales_channel_dict"]
    lvl1_products = filters["lvl_one_products"]

    # col1
    with col1:
        options_region_codes = st.multiselect("Регион", region_codes.keys())
        if not options_region_codes:
            options_region_codes = region_codes.keys()

        options_client = st.multiselect("Категория клиента", client_groups.keys())
        if not options_client:
            options_client = client_groups.keys()

        options_oneclick_flg = st.multiselect("Флаг oneclick", ["0", "1"])
        if not options_oneclick_flg:
            options_oneclick_flg = ["0", "1"]

    # col2
    with col2:
        options_products = st.multiselect("Продукт", products)
        if not options_products:
            options_products = products

        options_lvl1_products = st.multiselect("Продукт (1 уровня)", lvl1_products)
        if not options_lvl1_products:
            options_lvl1_products = lvl1_products

        options_appl_sales_channel = st.multiselect("Канал продажи", appl_sales_channel.keys())
        if not options_appl_sales_channel:
            options_appl_sales_channel = appl_sales_channel.keys()

    options_region_sql = "','".join([region_codes[reg] for reg in options_region_codes])
    options_client_sql = "','".join(list(itertools.chain.from_iterable([client_groups[cli] for cli in options_client])))
    options_oneclick_flg_sql = ",".join(options_oneclick_flg)
    options_products_sql = "','".join(options_products)
    options_lvl1_products_sql = "','".join(options_lvl1_products)
    options_appl_sales_channel_sql = "','".join(
        list(itertools.chain.from_iterable([appl_sales_channel[sch] for sch in options_appl_sales_channel])))

    # query
    region_ar = QueryMaker()
    region_ar.add_select("""
        date_trunc('month', appl_dt)::date as appl_month,
        coalesce(sum(issued_amt) / sum(approved_amt) * 100, 0) as take_up,
        coalesce(sum(approved_amt) / sum(reviewed_amt) * 100, 0) as ar,
        sum(case when issued_cnt = 1 then issued_amt else 0 end) as sum_issued
        """) \
        .add_table('rrb.dm_ll_appl_cp') \
        .add_where(
        f'product_type_id = \'1\' and (appl_dt::date between date \'{date_ar[0]}\' and date \'{date_ar[1]}\') '
        f'and region_code in (\'{options_region_sql}\') and appl_cust_group_code in (\'{options_client_sql}\')'
        f'and coalesce(appl_chanell_sales_code, -1488) in (\'{options_appl_sales_channel_sql}\') and '
        f'appl_product_lvl_2_text in (\'{options_products_sql}\') and '
        f'appl_terbank_name = \'Юго-Западный банк\' and appl_product_lvl_2_text <> \'Образовательный\' and '
        f'appl_product_lvl_1_text in (\'{options_lvl1_products_sql}\') and '
        f'oneclick_flg in ({options_oneclick_flg_sql})') \
        .add_group_by(f"date_trunc('month', appl_dt)::date")

    region_risk = QueryMaker()
    region_risk.add_select("""
        date_trunc('month', appl_dt)::date as appl_month,
        coalesce(sum(d7_from_first_pymnt_more_7d_ovr_flag * issue_rub_amt) / sum(issue_rub_amt) * 100, 0) as risk_7plus_1m,
        coalesce(sum(od_30_2_current) / sum(case when issued_cnt = 1 then issued_amt end) * 100, 0) as risk_30plus_2m,
        coalesce(sum(od_30_3_current) / sum(case when issued_cnt = 1 then issued_amt end) * 100, 0) as risk_30plus_3m,
        coalesce(sum(od_30_4_current) / sum(case when issued_cnt = 1 then issued_amt end) * 100, 0) as risk_30plus_4m,
        coalesce(sum(od_30_6_current) / sum(case when issued_cnt = 1 then issued_amt end) * 100, 0) as risk_30plus_6m
        """) \
        .add_table('rrb_pil.v_streamlit_ar_region_risk') \
        .add_where(
        f'product_type_id = \'1\' and (appl_dt::date between date \'{date_ar[0]}\' and date \'{date_ar[1]}\') '
        f'and region_code in (\'{options_region_sql}\') and appl_cust_group_code in (\'{options_client_sql}\')'
        f'and coalesce(appl_chanell_sales_code, -1488) in (\'{options_appl_sales_channel_sql}\') and '
        f'appl_product_lvl_2_text in (\'{options_products_sql}\') and '
        f'appl_terbank_name = \'Юго-Западный банк\' and appl_product_lvl_2_text <> \'Образовательный\' and '
        f'appl_product_lvl_1_text in (\'{options_lvl1_products_sql}\') and '
        f'oneclick_flg in ({options_oneclick_flg_sql})') \
        .add_group_by(f"date_trunc('month', appl_dt)::date")

    # dataframe
    df_ar_tu = conn.execute_sql_pd(region_ar.query)
    df_ar_tu = df_ar_tu.sort_values('appl_month')

    df_region_risk = conn.execute_sql_pd(region_risk.query)
    df_region_risk = df_region_risk.sort_values('appl_month')

    # show plot
    fig_ar_sum = px.bar(df_ar_tu, x='appl_month', y='ar', title='AR сумма')
    fig_tu = px.bar(df_ar_tu, x='appl_month', y='take_up', title='Take UP')
    fig_risk = px.line(df_region_risk, x='appl_month',
                       y=['risk_7plus_1m', 'risk_30plus_2m', 'risk_30plus_3m', 'risk_30plus_4m', 'risk_30plus_6m'],
                       title='Risk')
    fig_sum = px.bar(df_ar_tu, x='appl_month', y='sum_issued', title='Сумма выдач')

    with col1:
        st.plotly_chart(fig_ar_sum)
        st.plotly_chart(fig_risk)

    with col2:
        st.plotly_chart(fig_tu)
        st.plotly_chart(fig_sum)


if __name__ == '__main__':

    # page options
    st.set_page_config(
        page_title="Уровень одобрения ПК.ПРМ",
        layout="wide"
    )

    if 'st_started' in st.session_state:
        try:
            page_ar_reg()

        except Exception as e:
            st.warning(f"{e}")
            st.switch_page('Welcome.py')
            st.rerun()

    else:
        st.warning("Please login on welcome page")
