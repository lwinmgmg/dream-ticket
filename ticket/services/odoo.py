import aiohttp


class Odoo:
    def __init__(self, base_url: str, user: str, password: str) -> None:
        self.base_url = base_url
        self.user = user
        self.password = password

    async def get_odoo_user(self, token: str):
        async with aiohttp.ClientSession(base_url=self.base_url) as requests:
            async with requests.get(
                "/api_user/profile", headers={"Authorization": f"Odoo {token}"}
            ) as response:
                if response.status == 200:
                    resp: dict = await response.json()
                    return resp.get("login")
        return ""
