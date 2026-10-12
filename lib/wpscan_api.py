
from urllib.parse import quote

import requests

from lib.printer import warn


def lookup(kind, identifier, kwargs, response_key=None):
    token = kwargs.get('api_token')
    if not token:
        return None

    url = 'https://wpscan.com/api/v3/{}/{}'.format(kind, quote(identifier, safe=''))
    proxy = kwargs.get('proxy')
    try:
        response = requests.get(
            url,
            headers={'Authorization': 'Token token={}'.format(token)},
            timeout=kwargs.get('timeout') or 10,
            proxies={'http': proxy, 'https': proxy} if proxy else None,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError('unexpected JSON response')
        return data.get(response_key or identifier) or {}
    except (requests.RequestException, ValueError) as error:
        warn('WPScan API lookup failed for {} {}: {}'.format(kind, identifier, error))
        return None
