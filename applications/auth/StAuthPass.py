import streamlit_authenticator as stauth
from classes.FileOpener import FileOpener
import streamlit as st

class StAuthPass(FileOpener):

    def __init__(self):
        pass

    def get_auth(self, path: str) -> "auth":

        yaml_data = self.yaml_open(path)

        authenticator = stauth.Authenticate(
            yaml_data['credentials']
            , yaml_data['cookie']['name']
            , yaml_data['cookie']['key']
            , yaml_data['cookie']['expiry_days']
        )

        name, authentication_status, username = authenticator.login('Login', 'main')
        return name, authentication_status, username, authenticator