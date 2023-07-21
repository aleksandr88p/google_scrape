
import requests
BASE_URL = "https://api4serp.com/wp-json/mo/v1"
AUTH_KEY = "rtfXpi2HmCPg7DEBO233IepbBXG7Qdz9"
EXAMPLE_EMAIL = 'homarak409@msback.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    "Authorization": AUTH_KEY
    }


def get_all_users() -> dict:
    users_url = f'{BASE_URL}/getall'
    all_users = requests.get(users_url, headers=HEADERS).json()
    return all_users


def get_specific_user(email) -> dict:
    user_level_url = f'{BASE_URL}/getuser/{email}'
    specific_user = requests.get(user_level_url, headers=HEADERS).json()
    return specific_user


def change_available_request_value(email: str, new_value: str):
    change_url = f'{BASE_URL}/change_available_request?column_param1={email}&available_request={new_value}'
    requests.put(change_url, headers=HEADERS).json()


all_users = get_all_users()
print('printing all users')
for user in all_users:
    print(user)

specific_user = get_specific_user(EXAMPLE_EMAIL)
print('printing specific_user')
print(specific_user)

print('change available_request value for specific user')
change_available_request_value(EXAMPLE_EMAIL, '100')

specific_user = get_specific_user(EXAMPLE_EMAIL)
print('printing specific_user after change')
print(specific_user)