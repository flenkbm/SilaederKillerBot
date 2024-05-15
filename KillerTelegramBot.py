# importing libraries
import json
import time
from telebot import *


# preparing telebot
token = "none"  # I hid the token, because somebody can upload anthoer code for my bot
bot = TeleBot(token)


# accounts
class account:
    def __init__(self, login_, password_, name_, surname_, id_):
        self.login = login_
        self.password = password_
        self.name = name_
        self.surname = surname_
        self.id = id_
        self.chatid = 000
        self.targetid = ''
        self.targetname = ''
        self.kills = 0
        self.admin = False
        self.alive = True


accounts = dict()


# loading backup
def loadbackup():
    jsondata = open("last_backup.json", 'r')
    acc = json.load(jsondata)
    for i in acc.keys():
        accounts[i] = account('', '', '', '', '')
        accounts[i].login = acc[i][0]
        accounts[i].password = acc[i][1]
        accounts[i].name = acc[i][2]
        accounts[i].surname = acc[i][3]
        accounts[i].id = acc[i][4]
        accounts[i].chatid = acc[i][5]
        accounts[i].targetid = acc[i][6]
        accounts[i].targetname = acc[i][7]
        accounts[i].kills = acc[i][8]
        accounts[i].admin = acc[i][9]
        accounts[i].alive = acc[i][10]
    jsondata.close()
    return 0


loadbackup()


# varriables
game_chat = ""
chat_link = open("chatlink.txt", 'r')
game_chat = chat_link.readline()
chat_link.close()


# starting message
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет.\nЭто бот для игры киллер.\nОсновной чат игры: " +
                     game_chat + "\nТам же описаны и правила самой игры.\n\n\nРекоммендация к пользованию: при смене имени пользователя необходимо перезапустить бота во избежание его поломки (команда /start).")
    if (message.from_user.username not in accounts.keys()):
        bot.send_message(
            message.chat.id, 'Извините, но у меня нет аккаунта с вашим юзернеймом. Если вы поменяли юзернейм, отправьте мне комманду /change_username. Если у вас нет аккаунта, напишите комманду /register чтобы зарегистрироваться.')
    else:
        bot.send_message(
            message.chat.id, 'А, и ещё кое-что. Рад снова вас приветствовать, ' + accounts[message.from_user.username].name + ' ' + accounts[message.from_user.username].surname + '!')
        accounts[message.from_user.username].chatid = message.chat.id
        backup()
    return 0


# registratinging a new ccount
@bot.message_handler(commands=['register'])
def registration(message):
    bot.send_message(
        message.chat.id, 'Для создания нового аккаунта придумайте логин и пароль. Отправьте мне их в одном сообщении. Так же отправьте в этом сообщении мне свои имя и фамилию.\n\n\nФормат отправки:\n\nSuperLogin\nSuperPassword\nИван\nИванов')
    bot.register_next_step_handler(message, registration2)
    return 0


def registration2(message):
    if (len(message.text.split('\n')) != 4):
        error_input('/register', message.chat.id)
        return 0
    login, password, name, surname = message.text.split('\n')
    accounts[message.from_user.username] = account(
        login, password, name, surname, message.from_user.username)
    bot.send_message(
        message.chat.id, 'Регистраия прошла успешно! Пожалуйста, перезапустите бота для продолжения пользования (команада /start).')
    backup()
    return 0


# changing username
@bot.message_handler(commands=['change_username'])
def change_username(message):
    bot.send_message(
        message.chat.id, 'Для перепривязки аккаунта к другому юзернейму, отправьте ваши логин и пароль.\n\n\nФормат отправки:\n\nSuperLogin\nSuperPassword\n\n\nЕсли вы забыли ваши логин и пароль, отправьте мне сообщение:\n\n-1\n-1')
    bot.register_next_step_handler(message, change_username2)
    return 0


def change_username2(message):
    if (len(message.text.split('\n')) != 2):
        error_input('/change_username', message.chat.id)
    login, password = message.text.split('\n')
    for i in accounts.values():
        if (i.login == login):
            if (i.password == password):
                bot.send_message(
                    message.chat.id, 'Авторизация прошла успешно.')
                accounts[message.from_user.username] = i
                del accounts[i.id]
                accounts[message.from_user.username].id = message.from_user.username
                accounts[message.from_user.username].chatid = message.chat.id
                backup()
                bot.send_message(
                    message.chat.id, 'Имя пользователя успешно изменено')
                return 0
            else:
                bot.send_message(
                    message.chat.id, 'Ошибка! Неверный пароль.\nДля повторной попытки смены имени пользователя введите команду /change_username.')
                return 0
    bot.send_message(
        message.chat.id, 'Ошибка! Логин отсутствует в базе данных пользователей.\nДля повторной попытки смены имени пользователя введите команду /change_username.\n\nЕсли вы забыли свои логин и пароль, обратитесь к администраторам.')
    sendlistofadmins(message.chat.id)
    return 0


# killing
@bot.message_handler(commands=['kill'])
def kill(message):
    if (accounts[message.from_user.username].alive == False):
        bot.send_message(
            message.chat.id, 'Извините, но вы не можете более убивать в данном сезоне игры киллер, так как уже были убиты другим игроком.')
    bot.send_message(
        message.chat.id, 'Вы совершили убийство. Для подтверждения убийства введите имя и фамилию цели вашей жертвы в формате "Имя Фамилия" в именительном падеже с заглавной буквы (они написаны в килноуте вашей жертвы).')
    bot.register_next_step_handler(message, killing2)


def killing2(message):
    if (message.text == accounts[accounts[message.from_user.username].targetid].targetname):
        bot.send_message(
            message.chat.id, 'Убийство подтверждено. Ваша следующая цель указана в килноуте вашей жертвы.')
        #
        accounts[accounts[message.from_user.username].targetid].alive = False
        bot.send_message(
            accounts[accounts[message.from_user.username].targetid].chatid, 'К сожалению, вы были убиты игроком ' + accounts[message.from_user.username].name + ' ' + accounts[message.from_user.username].surname + '. В текущем сезоне вы больше не можете принимать участие. Желаю удачи в следующем сезоне.')
        #
        accounts[message.from_user.username].targetname = message.text
        accounts[message.from_user.username].targetid = accounts[accounts[message.from_user.username].targetid].targetid
        backup()
    else:
        bot.send_message(
            message.chat.id, 'Ошибка! Имя жертвы введено неверно. Для повторной попытки введите команду /kill ещё раз.')


# showing target's name
@bot.message_handler(commands=['target'])
def show_targetname(message):
    bot.send_message(message.chat.id, 'Ваша текущая цель: ' +
                     accounts[message.from_user.username].targetname)


# admin's commands
@bot.message_handler(commands=['cleanafterseazon', 'clean_after_seazon'])
def clean_after_seazon(message):
    if (accounts[message.from_user.username].admin):
        bot.send_message(
            message.chat.id, 'Процесс очистки бота после сезона начат.')
        #
        strangetime = time.ctime(time.time()).replace('  ', ' ').split()
        nowtime = strangetime[3].replace(':', '-')
        if (len(strangetime[2]) == 1):
            nowday = '0' + strangetime[2]
        else:
            nowday = strangetime[2]
        nowday += '-' + strangetime[1]
        nowday += '-' + strangetime[4]
        #
        finalfile = open("finalfile_" + nowday + ".txt", 'w')
        towrite = ''
        for i in accounts.values:
            towrite += i.name + ' ' + i.surname + ':\n' + 'Убийства: ' + \
                i.kills + '\n' + 'Жив: ' + i.alive + '\n\n'
        finalfile.write(towrite)
        finalfile.close()
        bot.send_message(
            message.chat.id, 'Данные текущего сезона сохранены.')
        #
        for i in accounts.values:
            i.targetname = ''
            i.targetid = ''
            i.kills = 0
            i.alive = True
        backup()
        #
        bot.send_message(
            message.chat.id, 'Бот успешно очищен и готов к старту нового сезона.')
        #
        for i in accounts.values():
            bot.send_message(
                i.chatid, 'ОПОВЕЩЕНИЕ:\nТекущий сезон киллера был завершён! Мы надеемся, что вам он понравился и ждём вас в следующем сезоне! Свои результаты вы можете посмотреть в прикреплённом ниже файле.')
            file = open("finalfile_" + nowday + ".txt", 'r')
            bot.send_message(
                i.chatid, file, filename="finalfile_" + nowday + ".txt")
            file.close()
    else:
        error_not_enough_acces(message.chat.id)
    return 0


@bot.message_handler(commands=['preparenewseazon', 'prepare_new_seazon'])
def warning_before_preparing_new_seazon(message):
    bot.send_message(
        message.chat.id, 'ВНИМАНИЕ! Перед созданием нового сезона необходимо произвести чистку после старого (команда /cleanafterseazon). Если вы этого ещё не сделали, отправьте -1, чтобы прервать выполнение команды.Так же убедитесь, что все игроки, которые участвуют в этом сезоне уже имеют аккаунты в боте, иначе автораспределение целей сработает некорректно. Если это не так, отправьте -1 для того, чтобы прервать выполнение команды. Если все вышеописанные условия соблюдены, отправьте 1, для продолжения выполнения команды.')
    bot.register_next_step_handler(message, preparing_new_sezon)


def preparing_new_sezon_midpart(message):
    if ((message.text != '1') and ((message.text != '-1'))):
        error_input(message.chat.id, '/preparenewseazon')
        return 0
    if (message.text == '-1'):
        bot.send_message(message.chat.id, 'Выполнение команды прервано.')
        return 0
    if (message.text == '1'):
        bot.send_message(
            message.chat.id, 'Начата подготовка нового сезона игры. . .')
        users = [i for i in accounts.keys()]
        for i in range(len(users)):
            if (i == len(users) - 1):
                accounts[users[i]].targetid = users[0]
            else:
                accounts[users[i]].targetid = users[i+1]
        for i in accounts.values():
            i.targetname = accounts[i.targetid].surname + \
                ' ' + accounts[i.targetid].name
        bot.send_message(
            message.chat.id, 'Пожалуйста, отправьте мне ссылку на чат нового сезона игры.')
        bot.register_next_step_handler(message, preparing_new_sezon_finalpart)
    return 0


def preparing_new_sezon_finalpart(message):
    if (message.text[:14] != 'https://t.me/'):
        bot.send_message(
            message.chat.id, 'Ошибка! Неправильная формат ссылки. Пожалуйста, отправьте ссылку заново.')
        bot.register_next_step_handler(message, preparing_new_sezon_finalpart)
        return 0
    game_chat = message.text
    chat_link = open("chatlink.txt", 'w')
    chat_link.write(game_chat)
    chat_link.close()
    backup()
    bot.send_message(
        message.chat.id, 'Подготовка нового сезона прошла успешно.')
    for i in accounts.values():
        bot.send_message(i.chatid, 'ОПОВЕЩЕНИЕ:\n\n\nНовый сезон игры киллер стартовал! Чат игры и правила можно найти по ссылке ' +
                         game_chat + '\nЖелаем вам удачной игры!')
        bot.send_message(
            i.chatid, 'P. s.:\nВаша текущая цель - ' + i.targetname + '\n\nПосмотреть имя вашей цели так же можно при помощи команды /target')
    return 0


# functions
def error_input(retry_command, chatid):
    bot.send_message(
        chatid, 'Ошибка! Неправильный формат отправки. Для повторной попытки введите команду ' + retry_command + ' ещё раз.')
    return 0


def error_not_enough_acces(chatid):
    bot.send_message(
        chatid, 'Ошибка! Недостаточный уровень доступа.\nМин. уровень доступа для выполнения действия: администратор.\nТекущий уровень доступа: пользователь.')
    return 0


def sendlistofadmins(chatid):
    bot.send_message(chatid, 'Список администраторов:\n' +
                     '\n@'.join([i.username for i in accounts if i.admin]))
    return 0


def backup():
    acc = dict()
    for i in accounts.keys():
        acc[i] = (accounts[i].login, accounts[i].password,
                  accounts[i].name, accounts[i].surname, accounts[i].id, accounts[i].chatid, accounts[i].targetid, accounts[i].targetname, accounts[i].kills, accounts[i].admin, accounts[i].alive)
    #
    nowtime = ''
    nowday = ''
    strangetime = time.ctime(time.time()).replace('  ', ' ').split()
    nowtime = strangetime[3].replace(':', '-')
    if (len(strangetime[2]) == 1):
        nowday = '0' + strangetime[2]
    else:
        nowday = strangetime[2]
    nowday += '-' + strangetime[1]
    nowday += '-' + strangetime[4]
    now = nowtime + '_' + nowday
    #
    timebackup_file = open(now + "_backup.json", 'w')
    json.dump(acc, timebackup_file)
    timebackup_file.close()
    #
    lastbackup_file = open("last_backup.json", 'w')
    json.dump(acc, lastbackup_file)
    lastbackup_file.close()
    #
    return 0


# infinity polling
bot.infinity_polling()
