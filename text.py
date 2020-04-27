HELP = '''Оперативно доносит о визитах избранных преподавателей в голосовые консультационные.

Использование: `command ...arguments`
Команды регистронезависимы.

О `fuzzy` аргументах:
Обрабатываются не по принципу "равно", но "больше всего похоже".
Например: из всех никнеймов преподавателей на сервере И5, `wolf` больше всего похож на `Woolfer#1420`.

Команды:
`add fuzzy_nickname ...`
    Подписывает вас на указанных _преподавателей_.
    e.g. `add c3h6o#7390 wolf`

`del fuzzy_nickname ...`
    Отписывает вас от кого вы там хотите.
    e.g. `del norte clcos першин`

`help`
    Выводит вот это вот все.
'''


READ_HELP = 'Вы неправы. Почитайте хелпарик (help).'


def found(user, channel):
    return f'{user} замечен в канале `{channel.name}`'


def add_report(subscribed_to):
    if len(subscribed_to) == 0:
        return 'Вы либо уже на всех подписаны, ' + \
               'либо мы таких не знаем:('

    else:
        return 'Подписали вас на:\n' + \
               '\n'.join(f'- {nickname}'
                         for nickname in subscribed_to)


def del_report(unsubscribed_from):
    if not unsubscribed_from:
        return 'Вы неправы.'
    else:
        return 'Отписали вас от:\n' + \
               '\n'.join(f'- {nickname}'
                         for nickname in unsubscribed_from)
