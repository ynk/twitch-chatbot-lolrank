import json
import os
from datetime import datetime
import pytz
import requests
import mastermind.config as config
import time

import urllib3

urllib3.disable_warnings()


class NotFound(Exception):
    pass


def sprint(msg):
    #if controller bot debug
    if config.Bot.debug:
        timeNow = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        print(f"[{timeNow}] {msg}")



def returnDanishTime():
    tz = pytz.timezone('Europe/Copenhagen')
    now = datetime.now(tz)
    return now.strftime("%H:%M:%S [%m/%d/%Y]")


def doRequest(url: str):
    global status_code
    for x in range(config.Riot.max_attempts):
        try:

            request = requests.get(url=url, verify=False, timeout=config.Riot.timeout,
                                   headers={'X-Riot-Token': config.Riot.api_key})

            if request.status_code == 200:
                return json.loads(request.content)
            elif request.status_code == 404:
                #print request url with api key
                sprint(f"Request url: {url}?api_key={config.Riot.api_key}")
                print(request.content)
                raise NotFound("No data was found")
            elif request.status_code == 401:
                print("??X?DD?XD")
            elif request.status_code == 429:

                retry = 5
                if 'Retry-After' not in request.headers:
                    time.sleep(retry)
                else:
                    retry = request.headers['Retry-After']
                    print(
                        f"doRequest:(attempt:{x}/{config.Riot.max_attempts}) sleeping "
                        f"for {retry} sec")
                    time.sleep(int(retry))
            else:
                status_code = request.status_code
                print(f"doRequest: {status_code} {request.text}")
        except NotFound as e:
            raise NotFound
        except Exception as e:
            print(e)


def save_config():
    with open("config.json", "w") as f:
        payload = {
            "last_msg": time.time()
        }
        f.write(json.dumps(payload))
        #print config saved
        sprint("Config saved.")



def load_config():
    payload = {
        "last_msg": time.time()
    }

    # check if config.json exists
    if not os.path.isfile("config.json"):
        sprint("Config file not found. Creating...")
        # create config file
        save_config()

    else:
        sprint("Config file found.")
        # load config.json
        with open("config.json", "r") as f:
            payload = json.loads(f.read())
            if "last_msg" not in payload:
                # print last msg send in datetime
                payload["last_msg"] = time.time()

    # print last_msg epoch in datetime
    sprint(f"Last msg: {datetime.fromtimestamp(payload['last_msg'])}")
    return payload


def check_if_cooldown_expired():
    #skip this is ran in debug
    if not config.Bot.debug:
        settings = load_config()
        last_msg = settings["last_msg"]
        calulation = (time.time() - last_msg)
        if calulation > config.Twitch.command_delay:
            sprint("cooldown expired")
            save_config()
            return True
        else:
            sprint("still on cooldown: " + str(calulation))
            return False
    else:

        return True



