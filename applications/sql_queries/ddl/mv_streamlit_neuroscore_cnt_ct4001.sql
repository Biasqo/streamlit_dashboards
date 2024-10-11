create materialized view rrb_pil.mv_streamlit_monitor_cnt_ct4001 as
(
with cte as (select gregor_dt,
                    model_calc_obj_sid,
                    model_calc_param_val as score_ct4001,
                    case
                        when model_calc_param_val > 0.0642 and model_calc_param_val <= 1 then '5'
                        when model_calc_param_val > 0.0262 and model_calc_param_val <= 0.0642 then '4'
                        when model_calc_param_val > 0.0133 and model_calc_param_val <= 0.0262 then '3'
                        when model_calc_param_val > 0.0065 and model_calc_param_val <= 0.0133 then '2'
                        when model_calc_param_val > 0.0023 and model_calc_param_val <= 0.0065 then '1'
                        when model_calc_param_val >= 0 and model_calc_param_val <= 0.0023 then '0'
                        else '-1'
                        end         as bucket_ct4001
             from ods_view.v_11_28_t_neuro_pim_txn_offline_rslt
             where model_calc_param_code = 'CT4001')
select gregor_dt::date as report_date_part,
       bucket_ct4001,
       count(*) as count_bundle
from cte
group by 1, 2
order by 1, 2)
        distributed by (report_date_part, bucket_ct4001);