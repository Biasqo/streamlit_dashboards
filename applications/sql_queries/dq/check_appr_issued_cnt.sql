select count(*)::integer as appl_cnt
    , sum(case when appl_status_code = '17' then 1 else 0 end)::integer as issued_cnt
    , appl_dt::date as appl_dt
from ods_view.v_05_13_t_applret_param
where appl_dt::date between '{}' and '{}'
group by 3
order by 3;