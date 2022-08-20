# twitch bot
import os
import wsgiref.handlers

import mastermind as controller
import mastermind.utils
from mastermind.utils import *
import mastermind.config as config

from twitchio.ext import commands




if config.Bot.debug:
    # print debug info
    sprint("Debug mode is enabled.")

settings = load_config()


class Bot(commands.Bot):
    def __init__(self):

        # When we init the bot, we are allowed to speak.
        # epoch last time we spoke
        self.last_time_spoke = settings['last_msg']  # Init our class with the time of now

        self.main_account = controller.functions.Riot.get_riot_account_by_puuid(config.Riot.StreamerAccount.account_id,
                                                                                "euw1")
        self.last_fetch_time = time.time()

        self.command_delay = 45
        super().__init__(token=config.Twitch.token, prefix=config.Twitch.prefix,
                         initial_channels=config.Bot.initial_channels)

    async def event_ready(self):
        sprint(f'Logged in as: {self.nick} in {config.Bot.initial_channels}')

    async def event_message(self, ctx: commands.Context):
        try:
            sprint(f"[{ctx.author.name}] {ctx.content}")

            await bot.handle_commands(ctx)
        except Exception as e:
            sprint(f"Exception: {e}")

    @commands.command()
    async def rank(self, ctx: commands.Context):
        # check if cooldown expired
        if mastermind.utils.check_if_cooldown_expired():
            # This block handles if we have to refetch the account or not
            if (time.time() - self.last_fetch_time) > 120:
                # fetch main account
                self.main_account = controller.functions.Riot.get_riot_account_by_puuid(
                    config.Riot.StreamerAccount.account_id, "euw1")
                self.main_account["fetched"] = time.time()

            else:
                sprint(
                    f"We don't have to (re)-fetch the main account yet. Wait {120 - (time.time() - self.last_fetch_time)} seconds.")

            self.main_account.get_ranked_stats()
            if self.main_account.solo_queue:
                await ctx.send(
                    f"{ctx.author.name} {self.main_account.name} is {self.main_account.solo_queue.tier} {self.main_account.solo_queue.rank}"
                    f" (W:{self.main_account.solo_queue.wins}) (L:{self.main_account.solo_queue.losses}) (LP: {self.main_account.solo_queue.lp}) (WR: {self.main_account.solo_queue.winrate} %) ")


    @commands.command()
    async def mmr(self, ctx: commands.Context):
        if mastermind.utils.check_if_cooldown_expired():
            mmr = mastermind.functions.Riot.get_riot_mmr_by_username_server(self.main_account.name, "euw1")

            if mmr:
                if "ranked" in mmr:
                    x = mmr['ranked']
                    await ctx.send(f"{ctx.author.name} {self.main_account.name} has an average mmr of {x['avg']} which "
                                   f"resembles {x['closestRank'].capitalize()} (guessed)")


    @commands.command()
    async def help(self, ctx: commands.Context):
        if mastermind.utils.check_if_cooldown_expired():
            await ctx.send(f"{ctx.author.name} you can use these commands to interact with me (!rank, !mmr)")


if __name__ == '__main__':
    if config.Bot.debug:
        sprint("!Debug mode is enabled. NO COMMAND RATE LIMIT!")
    bot = Bot()
    bot.run()
