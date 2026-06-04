import httpx

BRAWL_API_URL = "http://64.181.184.46:3000/v1"

class BrawlStarsService:
    """
    Serviço de conexão com a API do Brawl Stars.
    """

    async def get_player_data(self, player_tag: str):
        return await self._get_data("players", player_tag)

    async def get_club_data(self, club_tag: str):
        return await self._get_data("clubs", club_tag)

    async def _get_data(self, endpoint: str, bs_id: str):
        url = f"{BRAWL_API_URL}/{endpoint}/{bs_id}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as err:
                print(f"Erro ao conectar na VPS: {err}")
                return None