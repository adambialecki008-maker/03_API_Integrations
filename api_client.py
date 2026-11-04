import httpx
import os


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
    i = 1
    while True and limit > 0:
        posts = fetch_post_page(i, limit)
        all_posts.extend(posts)
        if len(posts) < limit:
            break
        i += 1
    return all_posts


if __name__ == "__main__":
    posts = fetch_all_posts()
    print(len(posts))
    print(type(posts[0]))
