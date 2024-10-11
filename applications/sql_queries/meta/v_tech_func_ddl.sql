create or replace view rrb_pil.v_tech_func_ddl as
(
SELECT n.nspname                        AS schema_name
     , p.proname                        AS function_name
     , pg_get_functiondef(p.oid)        AS func_def
     , pg_get_function_arguments(p.oid) AS func_args
     , pg_get_function_result(p.oid)    AS func_result
     , nspname
FROM pg_proc p
         JOIN pg_namespace n ON n.oid = p.pronamespace
);