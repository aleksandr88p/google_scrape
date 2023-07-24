
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
    change_url = f'{BASE_URL}/change_available_requests?column_param1={email}&available_requests={new_value}'
    requests.put(change_url, headers=HEADERS).json()

# def change_available_request_value(email: str, new_value: str):
#     change_url = f'{BASE_URL}/change_available_requests?column_param1={email}&available_requests={new_value}'
#     response = requests.put(change_url, headers=HEADERS)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error: {response.status_code} - {response.text}")


# all_users = get_all_users()
# print('printing all users')
# for user in all_users:
#     email = user['user_email']
#     unique_token = user['unique_token']
#     available_requests = user['available_requests']
#     print(email)
#     print(available_requests)
#     print(unique_token)
# print('**********************')
# specific_user = get_specific_user(EXAMPLE_EMAIL)
# specific_user = get_specific_user('gebamo5450@camplvad.com')
# print('printing specific_user')
# print(specific_user)

"""
printing specific_user
[{'submission_id': '8', 'user_email': 'homarak409@msback.com', 'submitted_on': '2023-07-14 06:14:18', 'unique_token': '116893152586096', 'available_requests': '998', 'last_reset_date': '2023-07-19 00:45:16'}]

"""
# print('change available_request value for specific user')
# change_available_request_value(EXAMPLE_EMAIL, '1110')
