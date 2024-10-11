import streamlit as st
from classes.ConnectToGP import ConnectToGP
from classes.DiagMaker import DiagMaker, COLOR_GRAPH, ENTITY_TYPES, NODE_GRAPH, get_data_error_deco
from streamlit_agraph import agraph, Node, Edge, Config

# @st.experimental_fragment
@st.cache_data(ttl=3600 * 8)
def render_graph(_func: "func"
                 , _conn: "connection"
                 , _config: Config
                 , tab_selected: str
                 , schema_selected: str
                 , entity_type: str) -> "agraph":
    nodes = []
    edges = []
    # init append
    nodes.append(
        Node(id=f'{schema_selected}.{tab_selected}'
             , label=f'{schema_selected}.{tab_selected}'
             , shape=NODE_GRAPH[entity_type]
             , color='#A020F0'
             , size=19
             )
    )
    nodes, edges = list(_func(conn=_conn, schema=schema_selected, name=tab_selected
                        , entity_type=entity_type, nodes=nodes, edges=edges, prev_object=[], ids=[]))[-1]
    return nodes,edges, _config

@st.cache_resource(ttl=3600 * 8)
def get_meta_data(_conn: "connection", query: str) -> list:
    return [val[0] for val in _conn.execute_sql_text(query)]

@get_data_error_deco
@st.cache_resource(ttl=3600 * 8)
def get_tab_meta(_conn: "connection", schema_selected: str, tab_selected: str) -> "list":
    tab_meta = _conn.execute_sql_pl(
        f"select column_name, data_type, column_description "
        f"from rrb_pil.v_tech_column_names "
        f"where table_schema = '{schema_selected}' "
        f"and table_name = '{tab_selected}'"
    )
    return tab_meta

def viz_agraphs() -> None:
    st.markdown("# Dev Diagrams")
    st.sidebar.header("Граф сбора объектов")
    # open files and connect
    props = st.session_state.props

    # init diag maker
    diag_maker = DiagMaker()

    # info
    info_text = "Таблицы ссылаются на функции с префиксом f_l_%ind%, иначе граф не будет построен дальше"
    st.markdown(f"""<div style="display: flex; align-items: center;"> 
            <span style="font-size: 24px; color: #007bff;">ℹ️
            </span> <span style="margin-left: 10px;">{info_text}</span> 
            </div> 
            """, unsafe_allow_html=True)

    # clear cache
    with st.sidebar:
        clear_cache_button = st.button("Обновить и очистить кэш")
        if clear_cache_button:
            st.cache_data.clear()
            get_meta_data.clear()
            st.write("Cache cleared")

    # connect
    conn = ConnectToGP(props["connect"]["host"], props["connect"]["database"], statement_timeout=30000)
    schemas = get_meta_data(_conn=conn, query="select nspname from pg_namespace")
    schema_selected = st.selectbox("Выберите схему", schemas, index=None,
                                   key="schema")
    tables = get_meta_data(_conn=conn, query=f"select table_name from information_schema.tables "
                                             f"where table_schema = '{schema_selected}'")
    tab_selected = st.selectbox("Выберите таблицу", tables, index=None, key="table")

    # columns
    col1, col2 = st.columns(2)

    if tab_selected:
        # get entity type
        entity_type = diag_maker.get_entity_type(conn=conn, schema=schema_selected, name=tab_selected)

        with col1:
            st.subheader(f'Схема сборки {ENTITY_TYPES[entity_type]} {tab_selected}')
            config = Config(width=800
                            , height=640
                            , graphviz_layout='neato'
                            , directed=True
                            , physics=False
                            , hierarchical=True
                            )
            nodes, edges, config = render_graph(_func=diag_maker.recursive_find_source
                                        , _conn=conn
                                        , _config=config
                                        , tab_selected=tab_selected
                                        , schema_selected=schema_selected
                                        , entity_type=entity_type
            )
            table_selected = agraph(nodes, edges, config)

        with col2:
            if table_selected and not any(item in table_selected for item in diag_maker.hdfs_src):
                tab_selected = table_selected.split('.')[1]
                schema_selected = table_selected.split('.')[0]
                entity_type = diag_maker.get_entity_type(conn=conn, schema=schema_selected, name=tab_selected)
            st.subheader(f'Поля и типы данных {ENTITY_TYPES[entity_type]} {tab_selected}')
            tab_meta = get_tab_meta(_conn=conn, schema_selected=schema_selected, tab_selected=tab_selected)
            st.dataframe(tab_meta, hide_index=True, use_container_width=True)

if __name__ == '__main__':
    # page options
    st.set_page_config(
        page_title="Графы и визуализация схем сбора таблиц",
        layout="wide"
    )

    if 'st_started' in st.session_state:
        # try:
        viz_agraphs()

        # except Exception as e:
        #     st.warning(f"{e}")
        #     st.switch_page('Welcome.py')
        #     st.rerun()

    else:
        st.warning("Please login on welcome page")