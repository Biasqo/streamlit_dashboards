select count(*) as cnt_appls
     , sum(case when coalesce(riskcost, 0) = 0 then 0 else 1 end) as sum_rc
     , application_date as appl_dt
from rrb_pil.dm_appls_metrics_recalc
where application_date::date between '{}' and '{}'
group by 3
order by 3 desc;