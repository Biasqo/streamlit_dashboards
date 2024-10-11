create or replace view rrb_pil.v_tech_exttab_info as
(
select relname, urilocation, writable
from pg_exttable
    join pg_class on pg_exttable.reloid = pg_class.oid
);