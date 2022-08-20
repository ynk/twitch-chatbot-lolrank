class Bot():
    initial_channels = ['yourtwitchchannelname']
    debug = False


class Twitch():
    token = "oauth:123"
    client_id = "l23456"
    prefix = "!"
    command_delay = 45





class Riot():
    api_key = "RGAPI-123"
    username_validation_pattern = "^[0-9\p{L} _.]{3,16}$"
    timeout = 30
    max_attempts = 2
    valid_servers = ['euw1', 'na1', 'eun1', 'br1',
                     'la1', 'la2', 'tr1', 'jp1', 'kr', 'ru', 'oc1']

    class StreamerAccount():
        account_id = "your_account_id"
        

    class Summoner():
        version = "v4"

