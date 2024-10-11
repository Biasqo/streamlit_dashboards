create or replace view rrb_pil.v_tech_column_names as
(
SELECT column_name,
       data_type,
       pg_catalog.col_description(format('%s.%s', isc.table_schema, isc.table_name)::regclass::oid,
                                  isc.ordinal_position) as column_description,
       table_name,
       table_schema
FROM information_schema.columns isc
);