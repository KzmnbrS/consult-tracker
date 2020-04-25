from itertools import filterfalse

import discord
import discord.utils


class VasyukovObserver(discord.Client):

    def __init__(self, subscribers):
        super().__init__()
        self.subscribers = subscribers

    ######################################################################
    # SECTION: Utility

    def user_for(self, **kwargs):
        return discord.utils.get(self.get_all_members(), **kwargs)

    def user_from(self, nickname):
        parts = nickname.split('#')
        if len(parts) != 2:
            return None
        return self.user_for(name=parts[0],
                             discriminator=parts[1])

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

    @staticmethod
    def validate_args(args, a=0, b=32, max_length=256):
        if len(args) < a or len(args) > b:
            return False

        for arg in args:
            if len(arg) > max_length:
                return False
        return True

    HELP = '''Использование: !consultTracker command ...arguments
    Команды:
    push nickname ...
        Подписывает вас на указанных _преподавателей_
        Пример: push c3h6o#7390 Woolfer#1420
        
    remove nickname ...
        Отписывает вас от кого вы там хотите
        Пример: remove c3h6o#7390 Woolfer#1420
    
    help
        Выводит вот это вот все 
    '''

    READ_HELP = 'Вы неправы. Почитайте хелпарик (!consultTracker help)'

    ######################################################################
    # SECTION: Event handlers

    async def on_message(self, message):
        if not message.content.startswith('!consultTracker'):
            return

        parts = message.content.split()
        if len(parts) < 2:
            await self.send_privately(self.READ_HELP, message.author)
            return

        command, args = parts[1], parts[2:]

        async def send_goodbytes():
            await self.send_privately(self.READ_HELP, message.author)

        if command == 'push':
            if not self.validate_args(args, 1):
                await send_goodbytes()
                return

            await self.handle_push(message.author, args)
        elif command == 'remove':
            if not self.validate_args(args, 1):
                await send_goodbytes()
                return

            await self.handle_remove(message.author, args)
        elif command == 'help':
            if not self.validate_args(args):
                await send_goodbytes()
                return

            await self.handle_help(message.author)

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
            message = f'{user} замечен в канале `{after.channel.name}`'
            await self.send_privately(message,
                                      self.user_for(id=subscriber))

    async def handle_push(self, author, nicknames):
        subscribed_to = []
        for user in filter(None, map(self.user_from, set(nicknames))):
            if not self.can_consult(user):
                continue

            pushed = await self.subscribers.push(author.id, user.id)
            if pushed:
                subscribed_to.append(str(user))

        if len(subscribed_to) == 0:
            message = 'Вы либо уже на всех подписаны, ' + \
                      'либо мы таких не знаем:('
            await self.send_privately(message, author)
        else:
            message = 'Подписали вас на:\n' + \
                      '\n'.join(f'- {nickname}' for nickname
                                in subscribed_to)
            await self.send_privately(message, author)

    async def handle_remove(self, author, nicknames):
        unsubscribed_from = []
        for user in filter(None, map(self.user_from, set(nicknames))):
            removed = await self.subscribers.remove(author.id, user.id)
            if removed:
                unsubscribed_from.append(str(user))

        if not unsubscribed_from:
            message = 'Вы неправы.'
            await self.send_privately(message, author)
        else:
            message = 'Отписали вас от:\n' + \
                      '\n'.join(f'- {nickname}' for nickname
                                in unsubscribed_from)
            await self.send_privately(message, author)

    async def handle_help(self, author):
        await self.send_privately(self.HELP, author)
