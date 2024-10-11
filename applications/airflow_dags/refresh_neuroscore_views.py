from airflow import DAG
from airflow.providers.se.greenplum.operators.greenplum import GreenplumOperatorSE
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
import time

args = {
    "owner": "20677888_omega-sbrf-ru",
    "greenplum_se_conn_id": "greenplum_se_gp_risk2",
    # это пойдёт в опции соединения (таймаут на длительность запроса/операции в 5 минут)
    "options": '-c statement_timeout=300000',
}
with DAG(
        dag_id="awf_pil_neuroscore_refresh_views",
        default_args=args,
        schedule_interval="0 3 * * *",
        start_date=days_ago(1),
        dagrun_timeout=timedelta(minutes=0),
        tags=["se", "greenplum_se", "clprm"],
        catchup=False,
) as dag:
    mv_streamlit_monitor_cnt_ct1002 = GreenplumOperatorSE(
        task_id="mv_streamlit_monitor_cnt_ct1002",
        greenplum_se_conn_id=dag.default_args.get("greenplum_se_conn_id"),
        retries=2,
        retry_delay=timedelta(minutes=7),
        sql="refresh materialized view rrb_pil.mv_streamlit_monitor_cnt_ct1002",
    )
    vacuum_mv_streamlit_monitor_cnt_ct1002 = GreenplumOperatorSE(
        task_id="vacuum_mv_streamlit_monitor_cnt_ct1002",
        greenplum_se_conn_id=dag.default_args.get("greenplum_se_conn_id"),
        retries=2,
        retry_delay=timedelta(minutes=7),
        sql="vacuum full rrb_pil.mv_streamlit_monitor_cnt_ct1002;",
        autocommit=True,
    )
    mv_streamlit_neuroscore_avg = GreenplumOperatorSE(
        task_id="mv_streamlit_neuroscore_avg",
        greenplum_se_conn_id=dag.default_args.get("greenplum_se_conn_id"),
        retries=2,
        retry_delay=timedelta(minutes=7),
        sql="refresh materialized view rrb_pil.mv_streamlit_neuroscore_avg",
    )
    vacuum_mv_streamlit_neuroscore_avg = GreenplumOperatorSE(
        task_id="vacuum_mv_streamlit_neuroscore_avg",
        greenplum_se_conn_id=dag.default_args.get("greenplum_se_conn_id"),
        retries=2,
        retry_delay=timedelta(minutes=7),
        sql="vacuum full rrb_pil.mv_streamlit_neuroscore_avg;",
        autocommit=True,
    )
    mv_streamlit_monitor_cnt_ct4001 = GreenplumOperatorSE(
        task_id="mv_streamlit_monitor_cnt_ct4001",
        greenplum_se_conn_id=dag.default_args.get("greenplum_se_conn_id"),
        retries=2,
        retry_delay=timedelta(minutes=7),
        sql="refresh materialized view rrb_pil.mv_streamlit_monitor_cnt_ct4001",
    )
    vacuum_mv_streamlit_monitor_cnt_ct4001 = GreenplumOperatorSE(
        task_id="vacuum_mv_streamlit_monitor_cnt_ct4001",
        greenplum_se_conn_id=dag.default_args.get("greenplum_se_conn_id"),
        retries=2,
        retry_delay=timedelta(minutes=7),
        sql="vacuum full rrb_pil.mv_streamlit_monitor_cnt_ct4001;",
        autocommit=True,
    )

    start = EmptyOperator(task_id="start")
    finish = EmptyOperator(task_id="finish")
    node = EmptyOperator(task_id="node")

    start >> [mv_streamlit_monitor_cnt_ct1002,
              mv_streamlit_neuroscore_avg,
              mv_streamlit_monitor_cnt_ct4001] \
    >> node \
    >> [vacuum_mv_streamlit_monitor_cnt_ct1002,
        vacuum_mv_streamlit_neuroscore_avg,
        vacuum_mv_streamlit_monitor_cnt_ct4001] \
    >> finish

if __name__ == "__main__":
    dag.cli()
