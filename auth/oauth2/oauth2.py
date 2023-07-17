from httpx_oauth.oauth2 import OAuth2
from typing import Optional, Tuple
import requests

# account_id, account_email = await oauth_client.get_id_email(

class YandexOAuth2(OAuth2):
    async def get_id_email(self, token: str) -> Tuple[str, Optional[str]]:

        response = requests.get('https://login.yandex.ru/info?format=json', headers={'Authorization': f'bearer {token}'}).json()
        return response['id'], response['default_email']
    
    async def get_id_login(self, token: str) -> Tuple[str, Optional[str]]:

        response = requests.get('https://login.yandex.ru/info?format=json', headers={'Authorization': f'bearer {token}'}).json()
        return response['login']
    