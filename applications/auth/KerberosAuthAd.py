import subprocess
import getpass

class KerberosAuthAd:

    def __init__(self):
        self.username_ad = getpass.getuser().split('_')[0]
        self.username_ipa = getpass.getuser()

    def kerberos_auth_ad(self, keytab_path: str) -> None:
        subprocess.call(['kinit', f'{self.username_ad}@OMEGA.SBRF.RU', '-kt', f'{keytab_path}'])

    def kerberos_auth_ipa(self, keytab_path: str) -> None:
        subprocess.call(['kinit', f'{self.username_ipa}@DF.SBRF.RU', '-kt', f'{keytab_path}'])