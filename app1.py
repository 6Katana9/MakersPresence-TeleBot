import telebot
from telebot import types
import requests
import datetime
import schedule, time as t
import json
from multiprocessing import Process



TOKEN='5357024980:AAGJJZ9NSQKdIlmENeDWYHZ3_x2GZWzpuVo'
BOT = telebot.TeleBot(TOKEN)


LOCATION_KB = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
LOCATION_KB.add(types.KeyboardButton(text="Точно", request_location=True))

NO_LOCATION_KB = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
NO_LOCATION_KB.add(types.KeyboardButton(text="Я в мейкерс"))


@BOT.message_handler(commands=["start"])
def start(message):
	BOT.send_message(message.chat.id, 'Нажми на кнопку', reply_markup=NO_LOCATION_KB)


@BOT.message_handler(content_types=['text'])
def _(message):
	if message.text.lower() == 'я в мейкерс':
		date = datetime.datetime.now()
		BOT.send_message(message.chat.id, 'Точно?', reply_markup=LOCATION_KB)
		BOT.register_next_step_handler(message, in_makers, x_date=date)
	else:
		text = 'Бот фиксирует время прихода.\nКак пользоваться?\n1.Включить геолокацию на телефоне\n2.Нажать на кнопку "Я в мейкерс", которая находится рядом с клавиатурой\nВНИМАНИЕ\n1.Бот не работает на TelegramDesktop, так как через комп нельзя отправить геоданные\n2.Обмануть систему не получится'
		BOT.send_message(message.chat.id, text)


def in_makers(message, x_date):
    print("➡ in_makers(message, date) :", _in_makers(message, x_date))


def send_msg_day():
	text = 'Успей отметиться'
	res = requests.get('https://check-mentors-crm.herokuapp.com/mentors/').json()
	for i in res:
		if i['telegram_id'] is not None and i["come_time"]=='09:55:00':
			BOT.send_message(i['telegram_id'], text)
	
def send_msg_ev():
	text = 'Успей отметиться'
	res = requests.get('https://check-mentors-crm.herokuapp.com/mentors/').json()
	for i in res:
		if i['telegram_id'] is not None and i["come_time"]=='18:15:00':
			BOT.send_message(i['telegram_id'], text)


def _in_makers(message, x_date, max_timeout=10):
	BOT.delete_message(message.chat.id, message.message_id)
	if message.forward_date == None:
		if message.location is not None and geocoder(message.location.latitude, message.location.longitude) == '29, Табышалиева улица, БП, Бишкек, 720222, Киргизия':
			date_ = message.date
			date = str(datetime.timedelta(seconds=date_)).split(", ")[-1]
			hour, minutes, seconds = date.split(":")
			hour = int(hour) + 6
			user_ = message.from_user.username
			id = message.from_user.id
			data = {
				'id':id,
				'time':f'{hour}:{minutes}:{seconds}',
				'username':user_ if user_ else 'dfgjbdgkhb'
			}
			timeset = (datetime.datetime.now() - x_date).seconds < max_timeout
			if timeset:
				res = requests.post(f'https://check-mentors-crm.herokuapp.com/check/', data)
				if res.status_code == 404:
					text = "Сори, тебя нет в бд"
				else:
					
					data = json.loads(res.text)
					time = data["time"]
					is_late = data["is_late"]
					if is_late:
						BOT.send_sticker(message.chat.id, 'CAACAgQAAxkBAAI-BWK-8TZ-QMul0nqWqgAB7vfD9UifGwACmQkAAj3E4VO02kKVUZJxEykE')
						text = f"Ты опоздал - {time}"
					else:
						BOT.send_sticker(message.chat.id, 'CAACAgQAAxkBAAI-CWK-8ULR7LmnogP9w0FMusB_EiOEAAIeCwACbZbRU5jjoxhIa6m4KQQ')
						text = f"Ты пришел вовремя - {time}"
			else:
				text = "Систему не наебееееешь"
		else:
			text = "Ты не на работе"
			BOT.send_sticker(message.chat.id, 'CAACAgQAAxkBAAI-DWK-9ZXnaWP6Saad7Rj9qMVaz-aWAALJCwACde_QU6WFK9dLr9r_KQQ')

		BOT.send_message(message.chat.id, text, reply_markup=NO_LOCATION_KB)
	else:
		BOT.send_message(message.chat.id, 'Систему не наебешь', reply_markup=NO_LOCATION_KB)


def geocoder(latitude, longitude):
    token = 'pk.31cdb9800922dd6090d90fba77e8bb57'
    headers = {"Accept-Language": "ru"}
    address = requests.get(f'https://eu1.locationiq.com/v1/reverse.php?key={token}&lat={latitude}&lon={longitude}&format=json', headers=headers).json()
    return address.get("display_name")
    

schedule.every().day.at("03:30:00").do(send_msg_day)
schedule.every().day.at("11:55:00").do(send_msg_ev)


def bot_proc():
    BOT.infinity_polling()

def send_proc():
	while True:
		schedule.run_pending()
		t.sleep(1)

if __name__ == '__main__':
	send_p = Process(target=send_proc, args=())
	send_p.start()
	bot_proc()


