import requests

import mastermind.config as config
from mastermind.DOT.RiotAccount import Summoner
import json

headers = {
    'User-Agent': "python:com.ynk.DiscordBot:v1.0.0",

}
class Riot():
    @staticmethod
    def get_riot_account(username: str, server: str):
        acc = Summoner(username, server)
        acc.get_ranked_stats()
        acc.get_mastery_data()

        return acc
    @staticmethod
    def get_riot_account_by_puuid(puuid: str, server: str):
        acc = Summoner(puuid, server)
        acc.get_ranked_stats()
        acc.get_mastery_data()

        print(f"Found account name {acc.name} on {acc.server} based on puuid: ")
        return acc

    @staticmethod
    def get_riot_mmr_by_username_server(username: str, server: str):
        url = f"https://euw.whatismymmr.com/api/v1/summoner?name={username}"
        print(url)
        mmr = {}
        try:
            mmrreq = requests.get(url,
                                  headers=headers, timeout=5)
            content = json.loads(mmrreq.content)
            for atr in ["ranked", "normal", "aram"]:
                if atr in content:
                    # Ranked object exists
                    mmr[atr] = {
                        "avg": content[atr]["avg"],
                        "closestRank": content[atr]["closestRank"]
                    }
                else:
                    mmr[atr] = "No data"

        except Exception as e:
            print(e)

        return mmr