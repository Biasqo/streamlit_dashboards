create materialized view rrb_pil.mv_streamlit_monitor_cnt_ct1002 as
(
with cte as (select gregor_dt,
                    model_calc_obj_sid,
                    model_calc_param_val as score_ct1002,
                    case
                        when model_calc_param_val > 0.8308 and model_calc_param_val <= 1 then '5'
                        when model_calc_param_val > 0.5927 and model_calc_param_val <= 0.8308 then '4'
                        when model_calc_param_val > 0.35 and model_calc_param_val <= 0.5927 then '3'
                        when model_calc_param_val > 0.1467 and model_calc_param_val <= 0.35 then '2'
                        when model_calc_param_val > 0.0311 and model_calc_param_val <= 0.1467 then '1'
                        when model_calc_param_val >= 0 and model_calc_param_val <= 0.0311 then '0'
                        else '-1'
                        end         as bucket_ct1002
             from ods_view.v_11_28_t_neuro_pim_txn_offline_rslt
             where model_calc_param_code = 'CT1002')
select gregor_dt::date as report_date_part,
       bucket_ct1002,
       count(*) as count_bundle
from cte
group by 1, 2
order by 1, 2
    )
        distributed by (report_date_part, bucket_ct1002);