from datetime import datetime
from dateutil.relativedelta import relativedelta

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

def change_last_reset_date(email: str, new_value: str):
    change_url = f'{BASE_URL}/change_last_reset_date?column_param1={email}&last_reset_date={new_value}'
    requests.put(change_url, headers=HEADERS)


current_datetime = datetime.now()


#######################
# check new functions #
#######################

# two_month_ago = current_datetime - relativedelta(months=2)
# new_val = two_month_ago.strftime("%Y-%m-%d %H:%M:%S")
# change_last_reset_date('gebamo5450@camplvad.com', new_value=new_val)


# all_users = get_all_users()
# for i in all_users:
#     print(i)

def reset_reqs_every_month():
    '''
    Reset available requests for all users every month.

    This function retrieves all users from the database, checks if one month
    has passed since their last reset date, and if so, sets their available
    requests to 1000 and updates the last reset date to the current date.

    :return: None
    '''
    all_users = get_all_users()
    for user_data in all_users:
        user_email = user_data['user_email']
        last_reset_date_str = user_data['last_reset_date']
        last_reset_date = datetime.strptime(last_reset_date_str, "%Y-%m-%d %H:%M:%S")
        one_month_ago = current_datetime - relativedelta(months=1)
        if current_datetime >= last_reset_date + relativedelta(months=1):
            change_available_request_value(user_email, '1000')
            new_last_reset_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # update last reset date
            change_last_reset_date(user_email, new_last_reset_date)


