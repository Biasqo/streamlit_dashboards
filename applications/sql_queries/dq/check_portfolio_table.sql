select appl_dt as appl_dt
    , count(*) as cnt_appls
from rrb_pil.dds_pil_default
where appl_dt::date between '{}' and '{}'
group by 1
order by 1 desc;