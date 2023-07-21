import aiohttp

BASE_URL = "https://api4serp.com/wp-json/mo/v1"
AUTH_KEY = "rtfXpi2HmCPg7DEBO233IepbBXG7Qdz9"
EXAMPLE_EMAIL = 'homarak409@msback.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    "Authorization": AUTH_KEY
}

async def get_all_users() -> dict:
    users_url = f'{BASE_URL}/getall'
    async with aiohttp.ClientSession() as session:
        async with session.get(users_url, headers=HEADERS) as response:
            all_users = await response.json()
    return all_users

async def get_specific_user(email) -> dict:
    user_level_url = f'{BASE_URL}/getuser/{email}'
    async with aiohttp.ClientSession() as session:
        async with session.get(user_level_url, headers=HEADERS) as response:
            specific_user = await response.json()
    return specific_user

async def change_available_request_value(email: str, new_value: str):
    change_url = f'{BASE_URL}/change_available_request?column_param1={email}&available_request={new_value}'
    async with aiohttp.ClientSession() as session:
        await session.put(change_url, headers=HEADERS)




all_users = await get_all_users()
print(all_users)
# Пример использования:
# async def main():
#     all_users = await get_all_users()
#     print('printing all users')
#     for user in all_users:
#         print(user)
#
#     specific_user = await get_specific_user(EXAMPLE_EMAIL)
#     print('printing specific_user')
#     print(specific_user)
#
#     print('change available_request value for specific user')
#     await change_available_request_value(EXAMPLE_EMAIL, '999')
#
#     specific_user = await get_specific_user(EXAMPLE_EMAIL)
#     print('printing specific_user after change')
#     print(specific_user)
#
# # Запуск асинхронной функции
# import asyncio
# asyncio.run(main())
