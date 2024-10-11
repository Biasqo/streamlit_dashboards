select round(avg(log_riskcost), 4)::float4 as avg_risk_cost
    , round(avg(case
                    when appl_status_code = '17' and req_type_text = 'appl'
                    then log_riskcost
                    end
            ), 4)::float4 as avg_risk_cost_issued
    , appl_dt::date as appl_dt
from rrb_pil.dds_pil_tsmr_appls
where (appl_dt::date between '{}' and '{}')
    and rn = 1
group by 3
order by 3;