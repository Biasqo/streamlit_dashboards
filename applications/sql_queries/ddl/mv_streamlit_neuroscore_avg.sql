create materialized view rrb_pil.mv_streamlit_neuroscore_avg as
(
with cte as (select gregor_dt,
                    model_calc_obj_sid,
                    max(case when model_calc_param_code = 'CT4001' then model_calc_param_val end) as score_CT4001,
                    max(case when model_calc_param_code = 'CT1002' then model_calc_param_val end) as score_CT1002
             from ods_view.v_11_28_t_neuro_pim_txn_offline_rslt
             where model_calc_param_code in ('CT1002', 'CT4001')
             group by 1, 2)
select gregor_dt::date as report_date_part,
       coalesce(avg(score_CT4001), 0)              as avg_CT4001,
       coalesce(avg(score_CT1002), 0)              as avg_CT1002,
       (count(*) - count(score_CT4001)) / count(*) as nulls_CT4001,
       (count(*) - count(score_CT1002)) / count(*) as nulls_CT1002,
       count(*)                                    as count_rows
from cte
group by 1
    )
        distributed by (report_date_part);