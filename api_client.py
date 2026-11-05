import httpx
import os
import time


def fetch_users() -> list[dict]:
    url = "https://jsonplaceholder.typicode.com/users"
    response = httpx.get(
        url=url,
        timeout=10.0,
    )
    response.raise_for_status()
    users = [
        {
            "id": data["id"],
            "name": data["name"],
            "email": data["email"],
        }
        for data in response.json()
    ]
    return users


def fetch_posts_by_user(user_id: int) -> list[dict]:
    url = "https://jsonplaceholder.typicode.com/posts"
    response = httpx.get(
        url=url,
        timeout=10.0,
        params={"userId": user_id},
    )
    response.raise_for_status()
    posts = [
        {
            "id": data["id"],
            "title": data["title"],
        }
        for data in response.json()
    ]
    return posts


def fetch_headers(api_key: str) -> dict:
    url = "https://httpbin.org/headers"
    response = httpx.get(
        url=url,
        timeout=10.0,
        headers={"X-API-KEY": api_key},
    )
    response.raise_for_status()
    results = response.json()["headers"]
    print(response.text)
    print(type(results))
    print(results.keys())
    return results


def get_api_key() -> str:
    api_key = os.getenv("API_KEY")
    if api_key is None or not api_key.strip():
        raise ValueError("No API Key")
    return api_key


def create_post(user_id: int, title: str, body: str) -> dict:
    post = {"userId": user_id, "title": title, "body": body}
    url = "https://jsonplaceholder.typicode.com/posts"
    response = httpx.post(
        url=url,
        json=post,
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def fetch_post_page(page: int, limit: int = 5) -> list[dict]:
    url = "https://jsonplaceholder.typicode.com/posts"
    params = {"_page": page, "_limit": limit}
    response = httpx.get(url=url, timeout=10.0, params=params)
    response.raise_for_status()
    results = [{"id": data["id"], "title": data["title"]} for data in response.json()]

    return results


def fetch_all_posts(limit: int = 10) -> list[dict]:
    all_posts = []
    page = 1
    while True and limit > 0:
        posts = fetch_post_page(page, limit)
        all_posts.extend(posts)
        if len(posts) < limit:
            break
        page += 1
    return all_posts


def fetch_post_page_with_retry(
    page: int, limit: int = 5, max_attempts: int = 3
) -> list[dict]:
    results = []
    if max_attempts <= 0:
        raise ValueError("Max_attempts value must be > 0")
    for attempt in range(max_attempts):
        try:
            delay_seconds = 2**attempt
            results = fetch_post_page(page, limit)
            break
        except httpx.TimeoutException as e:
            if attempt >= max_attempts - 1:
                raise
            time.sleep(delay_seconds)
        except httpx.HTTPStatusError as error:
            if attempt >= max_attempts - 1:
                raise
            status = error.response.status_code
            if status == 429:
                delay = error.response.headers.get("Retry-After")
                if delay is not None and delay.isdecimal():
                    delay_seconds = int(delay)
            elif status != 500:
                raise
            time.sleep(delay_seconds)
    return results


def fetch_bearer_profile(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://httpbin.org/bearer"
    response = httpx.get(url=url, headers=headers, timeout=10.0)
    response.raise_for_status()
    return response.json()


def fetch_access_token(client_id: str, client_secret: str) -> str:
    url = "https://auth.example.com/oauth/token"
    data = {"grant_type": "client_credentials"}
    auth = (client_id, client_secret)
    response = httpx.post(url=url, data=data, auth=auth, timeout=10.0)
    response.raise_for_status()
    results = response.json()
    token = results["access_token"]
    return token


def fetch_protected_data(client_id: str, client_secret: str) -> dict:
    url = "https://api.example.com/data"
    token = fetch_access_token(client_id=client_id, client_secret=client_secret)
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(url=url, timeout=10.0, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    fetch_access_token("1", "test")
