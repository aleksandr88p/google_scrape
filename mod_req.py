# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import ssl
from asyncio import TimeoutError

import aiohttp
from aiohttp.client_exceptions import (
    ServerTimeoutError, ServerDisconnectedError, TooManyRedirects, ClientConnectorError
)
from aiohttp_socks import ProxyConnector
from python_socks._errors import ProxyError, ProxyTimeoutError
import certifi

class ResponseReq:
    status = int
    headers = dict
    cookies = dict
    real_url: str = ''
    text = str = ''


class AsyncReq:
    def __init__(self):
        self.headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,ko;q=0.6',
        }
        timeout_sec = 10
        self.sslcontext = ssl.create_default_context(cafile=certifi.where())
        self.session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_sec, sock_read=timeout_sec + 20)

    @staticmethod
    async def get_response(resp):
        rea = ResponseReq()
        try:
            if isinstance(resp, aiohttp.client_reqrep.ClientResponse):
                rea.status = resp.status
                rea.headers = resp.headers
                rea.cookies = {key: cookie.value for key, cookie in resp.cookies.items()}
                rea.real_url = str(resp.url)
                # rea.cookies = {key: cookie for key, cookie in resp.cookies.items()}
                # rea.cookies = resp.cookies.get_dict()
                rea.text = await resp.text()
            elif isinstance(resp, str):
                if resp == 'TooManyRedirects':
                    rea.status = 404
                elif resp == 'ProxyError':
                    rea.status = 503
        except TimeoutError:
            return None
        except Exception as e:
            logging.debug(e)
            return None
        return rea

    async def return_responses(self, url, headers=None, cookies=None, proxies=None, data=None, params=None):
        result = None
        if headers is None:
            headers = self.headers
        try:
            connector = ProxyConnector.from_url(proxies) if proxies else None
            async with aiohttp.ClientSession(connector=connector, timeout=self.session_timeout,
                                             headers=headers, cookies=cookies) as session:
                if data is None:
                    async with session.get(url=url, params=params,
                                           data=data, ssl=self.sslcontext) as response:
                        result = await self.get_response(resp=response)
                else:
                    async with session.post(url=url, data=data, params=params, ssl=self.sslcontext) as response:
                        result = await self.get_response(resp=response)
        except (ProxyTimeoutError, ServerTimeoutError, ServerDisconnectedError, ClientConnectorError):
            pass
        except TooManyRedirects:
            result = await self.get_response(resp='TooManyRedirects')
        except ProxyError:
            result = await self.get_response(resp='ProxyError')
        except Exception as e:
            logging.debug(f"{url} | {params} | {e}")
        finally:
            return result

    @staticmethod
    async def gather_with_concurrency(n, *coros):
        semaphore = asyncio.Semaphore(n)

        async def sem_coro(coro):
            async with semaphore:
                return await coro

        return await asyncio.gather(*(sem_coro(c) for c in coros))
