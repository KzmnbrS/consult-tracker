from itertools import filterfalse

import discord
import discord.utils

from fuzzywuzzy import process

from validate import ValidationError, with_arguments
from text import *


class VasyukovObserver(discord.Client):

    def __init__(self, subscribers):
        super().__init__()
        self.trainer_nicknames = {}
        self.subscribers = subscribers

    async def update_trainer_nicknames(self):
        self.trainer_nicknames = {}
        for user in self.get_all_members():
            if self.can_consult(user):
                self.trainer_nicknames[str(user)] = user

    on_ready = update_trainer_nicknames
    on_guild_join = update_trainer_nicknames
    on_guild_remove = update_trainer_nicknames
    on_guild_update = update_trainer_nicknames

    ######################################################################
    # SECTION: Utility

    def user_for(self, **kwargs):
        return discord.utils.get(self.get_all_members(), **kwargs)

    def trainer_like(self, query):
        key, _ = process.extractOne(query, self.trainer_nicknames.keys())
        return self.trainer_nicknames[key]

    @staticmethod
    def can_consult(user):
        for role in user.roles:
            if role.name in ('staff', 'admin'):
                return True
        return False

    @staticmethod
    def is_consultation_room(value):
        return value.startswith('Консультационная')

    @staticmethod
    async def send_privately(message, user):
        channel = user.dm_channel
        if channel is None:
            channel = await user.create_dm()
        await channel.send(message)

    ######################################################################
    # SECTION: Event handlers

    async def on_message(self, message):
        # Fires even for the bot's messages in direct channels
        if message.author.id == self.user.id:
            return

        async def send_goodbytes():
            await self.send_privately(READ_HELP, message.author)

        parts = message.content.split()
        command, args = parts[0].lower(), parts[1:]

        try:
            if command == 'add':
                await self.handle_add(message.author, args)
            elif command == 'del':
                await self.handle_del(message.author, args)
            elif command == 'help':
                await self.handle_help(message.author)
            else:
                await send_goodbytes()
        except ValidationError:
            await send_goodbytes()

    async def on_voice_state_update(self, user, _, after):
        # !channel.join event
        if after.channel is None:
            return

        if not self.is_consultation_room(after.channel.name):
            return

        if not self.can_consult(user):
            return

        subscribers = await self.subscribers.list(user.id)
        for subscriber in subscribers:
            await self.send_privately(found(user, after.channel),
                                      self.user_for(id=subscriber))

    @with_arguments(a=1)
    async def handle_add(self, author, nicknames):
        subscribed_to = []
        for user in filter(None, map(self.trainer_like, set(nicknames))):
            pushed = await self.subscribers.push(author.id, user.id)
            if pushed:
                subscribed_to.append(str(user))
        await self.send_privately(add_report(subscribed_to), author)

    @with_arguments(a=1)
    async def handle_del(self, author, nicknames):
        unsubscribed_from = []
        for user in filter(None, map(self.trainer_like, set(nicknames))):
            removed = await self.subscribers.remove(author.id, user.id)
            if removed:
                unsubscribed_from.append(str(user))
        await self.send_privately(del_report(unsubscribed_from), author)

    async def handle_help(self, author):
        await self.send_privately(HELP, author)
