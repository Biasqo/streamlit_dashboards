select sum(case when message_type = 'REQUEST' then 1 else 0 end)::integer as rq_count,
       sum(case when message_type = 'RESPONSE' then 1 else 0 end)::integer as rs_count,
       save_timestamp_prom::date as cv_ucl_date
from rrb_pil.tech_log_ezht_codes
where bs_code = 'CV_UCL_MEF' and (save_timestamp_prom::date between '{}' and '{}')
group by 3
order by 3;