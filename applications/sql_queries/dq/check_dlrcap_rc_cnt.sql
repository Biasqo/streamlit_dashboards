select count(risk_cost_md_risk_cost)::integer as count_risk_cost, timestampcolumn::date as timestampcolumn
from rrb.dds_ll_rr_cp_attrs_pil
where (timestampcolumn::date between '{}' and '{}')
    and coalesce(risk_cost_md_risk_cost, 0) = 0
group by 2
order by 2;