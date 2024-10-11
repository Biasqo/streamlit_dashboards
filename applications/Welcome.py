import streamlit as st
from auth.KerberosAuthAd import KerberosAuthAd
from auth.StAuthPass import StAuthPass
from classes.FileOpener import FileOpener
import psutil
import plotly.express as px

if __name__ == '__main__':

    # pages config
    st.set_page_config(
        page_title="Welcome page",
        page_icon="Welcome",
    )

    # open file
    available_vmem = round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total, 2)
    file_opener = FileOpener()
    props = file_opener.json_open("properties/properties.json")
    filters = file_opener.json_open("filters/filters.json")
    blacklist = file_opener.txt_open("data/blacklist.txt")

    # session states
    st.session_state.props = props
    st.session_state.filters = filters
    st.session_state.available_vmem = available_vmem
    st.session_state.blacklist = blacklist

    # streamlit auth
    st_auth = StAuthPass()
    name, authentication_status, username, authenticator = st_auth.get_auth(props["secrets_path"])

    if authentication_status:
        authenticator.logout('Logout', 'main')
        if 'st_started' not in st.session_state:
            with st.spinner("Стартуем"):
                st.session_state['st_started'] = True
        # kerberos auth
        kerberos_auth = KerberosAuthAd()
        kerberos_auth.kerberos_auth_ad(props["kerberos_data"]["ad"])

        # start page
        st.write("# Добро пожаловать на стартовую страницу CLPRM.BI")
        st.markdown(
            """
                Это приветственная страница
                ### Git'ы проекта
                - [clprm_de_git](https://df-bitbucket.ca.sbrf.ru/projects/CLPRM_DE)
                - [streamlit](https://df-bitbucket.ca.sbrf.ru/projects/CLPRM_DE/repos/streamlit_current/browse)
            """
        )
        st.plotly_chart(
            px.pie(values=[psutil.cpu_percent(), 100 - psutil.cpu_percent()],
                   names=["Used CPU", "Free CPU"],
                   color=["Used CPU", "Free CPU"],
                   color_discrete_map={"Used CPU": "hotpink", "Free CPU": "lightgreen"},
                   hole=0.5)
        )
        st.plotly_chart(px.pie(values=[psutil.virtual_memory().percent, 100 - psutil.virtual_memory().percent],
                               names=["Used VMEM", "Free VMEM"],
                               color=["Used VMEM", "Free VMEM"],
                               color_discrete_map={"Used VMEM": "hotpink", "Free VMEM": "lightgreen"},
                               hole=0.5)
        )
        
    elif authentication_status == False:
        st.error('Username/password is incorrect')
        try:
            del st.session_state['st_started']
        except:
            pass
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        try:
            del st.session_state['st_started']
        except:
            pass