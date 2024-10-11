import os
from streamlit_agraph import agraph, Node, Edge, Config
import re
import streamlit as st

def get_data_error_deco(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # st.info(f'while processing got an error: {e.__context__}')
            return []

    return wrapper

ENTITY_TYPES = {
    "BASE TABLE": "таблицы",
    "VIEW": "представления",
    "EXT TABLE": "внешней таблицы",
    None: "o_ таблицы"
}

COLOR_GRAPH = {
    "EXT TABLE": "#ffc300",
    "BASE TABLE": "#00bfff",
    "VIEW": "#e6e6fa",
    "HADOOP TABLE": "#ff6f61",
    None: "#00bcff"
}

NODE_GRAPH = {
    "EXT TABLE": "hexagon",
    "BASE TABLE": "square",
    "VIEW": "triangle",
    "HADOOP TABLE": "diamond",
    None: "square"
}

HDFS_SRC = ['prx', 'pxf']

class DiagMaker:
    def __init__(self):
        self.entity_types = ENTITY_TYPES
        self.color_graph = COLOR_GRAPH
        self.node_graph = NODE_GRAPH
        self.hdfs_src = HDFS_SRC

    @staticmethod
    @get_data_error_deco
    def get_entity_type(conn: "connection", schema: str, name: str) -> str:
        # check if it is a table
        entity_type = [val[0] for val in conn.execute_sql_text(f"select table_type from information_schema.tables "
                                                               f"where table_schema = '{schema}' "
                                                               f"and table_name = '{name}'")]
        if entity_type:
            if entity_type[0] == 'BASE TABLE':
                external_tab = [val[0] for val in
                                conn.execute_sql_text(f"select relname from rrb_pil.v_tech_exttab_info "
                                                      f"where relname = '{name}'")]
                if external_tab:
                    entity_type = ['EXT TABLE']
            return entity_type[0]
        else:
            return None

    @staticmethod
    @get_data_error_deco
    def get_chain_object(conn: "connection", schema: str, name: str, entity_type: str) -> list:
        if entity_type == 'BASE TABLE':
            pattern = r'\b(?:from|join)\s+(\w+\.\w+)'
            function_ddl = [val[0] for val in conn.execute_sql_text(f"select func_def from rrb_pil.v_tech_func_ddl "
                                                                    f"where nspname = '{schema}' "
                                                                    f"and function_name ilike 'f_l_%%{name}'")]
            if function_ddl:
                result = []
                for ddl in function_ddl:
                    sql_statement = ddl.lower().replace('\n', ' ')
                    result = result + list(set(re.findall(pattern, sql_statement)))
                return result
            else:
                return []
        elif entity_type == 'VIEW':
            pattern = r'\b(?:from)\s+(\w+\.\w+)'
            view_ddl = [val[0] for val in conn.execute_sql_text(f"select pg_get_viewdef('{schema}.{name}')")]
            if view_ddl:
                result = re.findall(pattern, view_ddl[0].lower())
                return result
            else:
                return []
        elif entity_type == 'EXT TABLE':
            exttab_ddl = [val[0] for val in conn.execute_sql_text(f"select urilocation "
                                                                  f"from rrb_pil.v_tech_exttab_info "
                                                                  f"where relname = '{name}'")]
            if exttab_ddl:
                return exttab_ddl[0]
            else:
                return []

    @staticmethod
    @get_data_error_deco
    def recursive_find_source(conn: "connection"
                              , schema: str
                              , name: str
                              , entity_type: str
                              , nodes: list
                              , edges: list
                              , prev_object: list
                              , ids: list) -> None:
        objects = DiagMaker.get_chain_object(conn=conn, schema=schema, name=name, entity_type=entity_type)
        prev_object.append(f'{schema}.{name}')
        objects = list(set([x for x in objects if x not in prev_object]))
        prev_object = list(set(prev_object + objects))

        if objects:
            for val in objects:
                if any(item in val for item in HDFS_SRC):
                    val_entity_type = 'HADOOP TABLE'
                    stop_iter = True
                else:
                    val_entity_type = DiagMaker.get_entity_type(conn=conn, schema=val.split('.')[0],
                                                                name=val.split('.')[1])
                    stop_iter = False
                if val not in ids:
                    nodes.append(
                        Node(id=f'{val}'
                             , label=f'{val}'
                             , shape=NODE_GRAPH[val_entity_type]
                             , color=COLOR_GRAPH[val_entity_type]
                             , size=19
                             )
                    )
                    ids.append(val)

                edges.append(
                    Edge(source=f'{schema}.{name}',
                         target=f'{val}')
                )
                if stop_iter:
                    yield [nodes, edges]
                else:
                    if val_entity_type:
                        yield from DiagMaker.recursive_find_source(conn=conn
                                                                   , schema=val.split('.')[0]
                                                                   , name=val.split('.')[1]
                                                                   , entity_type=val_entity_type
                                                                   , nodes=nodes
                                                                   , edges=edges
                                                                   , prev_object=prev_object
                                                                   , ids=ids)
                    else:
                        yield [nodes, edges]
        else:
            yield [nodes, edges]