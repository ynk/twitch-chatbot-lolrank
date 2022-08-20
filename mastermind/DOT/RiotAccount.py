import json
import re

import mastermind.config
import mastermind.utils as utils


class Validation:
    class ServerInvalidError(Exception):
        pass

    class UsernameInvalidError(Exception):
        pass


class Summoner(object):
    def __init__(self, username, server):

        self.username = username
        self.server = server

        self.id = None
        self.accountId = None
        self.puuid = None
        self.name = None
        self.profileIconId = None
        self.revisionDate = None
        self.summonerLevel = None
        self._id = None

        self._username = None

        self._server = None
        self.payload = {}

        # Json dict
        self.summoner = None
        self.mastery = []
        self.ranked = None

        self.solo_queue = Ranked(None)
        self.flex_queue = Ranked(None)

        if len(username) == 78:
            self.puuid = self.username
            self.get_summoner_by_id()
        else:
            # check if length of username is not longer than 16
            if len(username) > 16:
                raise Validation.UsernameInvalidError("Username is too long")
            self.get_summoner()

    def get_summoner(self):
        url = f"https://{self.server}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{self.username}"

        response = utils.doRequest(url)

        if response:
            self.summoner = response
            self.parse_summoner_object(self.summoner)

    def parse_summoner_object(self, response):
        try:
            self.id = response['id']
            self.accountId = response['accountId']
            self.puuid = response['puuid']
            self.name = response['name']
            self.profileIconId = response['profileIconId']
            self.revisionDate = response['revisionDate']
            self.summonerLevel = response['summonerLevel']
            self._id = response['id']
            self._username = response['name']

        except Exception as e:
            print(f"parse_summoner_object: {e}")
            return False

    def get_ranked_stats(self):
        url = f"https://{self.server}.api.riotgames.com/lol/league/v4/entries/by-summoner/{self.id}"
        try:
            response = utils.doRequest(url)
            if response:
                for data in response:
                    if data['queueType'] == "RANKED_SOLO_5x5":
                        self.solo_queue = Ranked(data)
                    elif data['queueType'] == "RANKED_FLEX_SR":
                        self.flex_queue = Ranked(data)

        except Exception as e:
            print(e)
            return None

    def get_mastery_data(self):
        url = f"https://{self.server}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{self.id}"
        response = utils.doRequest(url)
        if response:
            unsorted = []
            sorted_list = []
            for key in response:
                try:
                    unsorted.append(Champion(key).data)
                except Exception as e:
                    print(e)
                    continue

            try:
                sorted_list = sorted(unsorted, key=lambda k: k['championPoints'], reverse=True)
            except Exception as e:
                print(e)

            self.mastery = sorted_list
            return self.mastery

    def __str__(self):
        self.payload["summoner"] = self.summoner

        self.payload["ranked"] = {"solo": self.solo_queue.data, "flex": self.flex_queue.data}
        self.payload["mastery"] = self.mastery
        return json.dumps(self.payload, indent=4)

    def get_summoner_by_id(self):
        print(
            "Puuid is being used instead of username since the length was too long so I assume we don't know the actual account name")
        url = f"https://{self.server}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{self.puuid}"

        response = utils.doRequest(url)
        if response:
            self.summoner = response

            self.parse_summoner_object(self.summoner)
        else:
            print("No summoner found")


class Ranked(object):
    def __init__(self, data):
        if data:
            self.tier = str(data['tier']).capitalize()
            self.rank = str(data['rank'])
            self.lp = int(data['leaguePoints'])
            self.wins = int(data['wins'])
            self.losses = int(data['losses'])
            self.winrate = round((self.wins / (self.wins + self.losses)) * 100, 2)

            self.data = {
                "tier": self.tier,
                "rank": self.rank,
                "lp": self.lp,
                "wins": self.wins,
                "losses": self.losses,
                "winrate": self.winrate,

            }
        else:
            self.data = None

    def __str__(self):
        return json.dumps(self.data, indent=4)


class Champion(object):
    def __init__(self, data):
        if data:
            self.championId = int(data['championId'])
            self.championLevel = int(data['championLevel'])
            self.championPoints = int(data['championPoints'])
            self.lastPlayTime = int(data['lastPlayTime'])
            self.lastPlayTimeUTC = None
            self.chestGranted = bool(data['chestGranted'])
            self.tokensEarned = int(data['tokensEarned'])
            self.summonerId = str(data['summonerId'])
            self.data = {
                "championId": self.championId,
                "championLevel": self.championLevel,
                "championPoints": self.championPoints,
                "lastPlayTime": self.lastPlayTime,
                "lastPlayTimeUTC": self.lastPlayTimeUTC,
                "chestGranted": self.chestGranted,
                "tokensEarned": self.tokensEarned,
                "summonerId": self.summonerId,
            }
        else:
            self.data = None

    def __str__(self):
        return json.dumps(self.data, indent=4)
