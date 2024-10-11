create or replace view rrb_pil.v_streamlit_ar_region_risk as
(
select cp.*,
       ri.issue_rub_amt,
       ri.d7_from_first_pymnt_more_7d_ovr_flag,
       d.od_30_2_current,
       d.od_30_3_current,
       d.od_30_4_current,
       d.od_30_6_current
from rrb.dm_ll_appl_cp cp
         left join rrb_pil.dds_pil_default d on cp.appl_num::text = d.appl_num::text
         left join ods_view.v_04_12_t_cred_rsk_indctr ri on cp.appl_num::text = ri.appl_num::text
    );