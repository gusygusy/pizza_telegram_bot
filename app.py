from flask import Flask, request
import telegram
from transitions import Machine
from telegram.ext import ConversationHandler
from t_bot.cred import bot_token, bot_user_name, URL
import re
import logging
logging.basicConfig(level=logging.DEBUG)

logging.getLogger('transitions').setLevel(logging.INFO)

bot_ = telegram.Bot(token=bot_token)

app = Flask(__name__)

class Order(object):
    def __init__(self):
        pass

    def set_id(self, id):
        super().__setattr__('id', id)

    def set_size(self, size):
        super().__setattr__('size', size)

    def set_payment_type(self, p_type):
        super().__setattr__('p_type', p_type)

    def throw_to_db(self):
        """" func to throw order details in db (ToDo)"""
        pass


class Storage(object):
    def ask_dims(self, chat_id, msg_id):
        size = "Какую пиццу Вы хотите - маленькую или большую?"
        bot_.sendMessage(chat_id=chat_id, text=size, reply_to_message_id=msg_id)
        return

    def ask_how(self, chat_id, msg_id):
        size = "Как Вы будете платить ?"
        bot_.sendMessage(chat_id=chat_id, text=size, reply_to_message_id=msg_id)
        return

    def affirm(self, size, payment, chat_id, msg_id):
        aff = f"Вы хотите {size} пиццу, оплата {payment} ?"
        bot_.sendMessage(chat_id=chat_id, text=aff, reply_to_message_id=msg_id)
        return

    def gratitude(self, chat_id, msg_id):
        tnx = "Спасибо за заказ"
        bot_.sendMessage(chat_id=chat_id, text=tnx, reply_to_message_id=msg_id)
        return
    
    def refuse(self, chat_id, msg_id):
        ref = "Заказ отменен"
        bot_.sendMessage(chat_id=chat_id, text=ref, reply_to_message_id=msg_id)
        return

    def clean(self): return

ord = Order()
fs = Storage()
machine = Machine(model=fs, states=['nap', 'ask_which', 'ack', 'half_nap'],
                        initial='nap')
machine.add_transition('new_order', 'nap', 'ask_which')

machine.on_enter_ask_which('ask_dims')

machine.add_transition('consent', 'ask_which', 'ack', before='ask_how')

machine.add_transition('to_bed', 'ack', 'half_nap', before='affirm' )
machine.add_transition('sleep', 'half_nap', 'nap', before='gratitude')
machine.add_transition('on_refuse', '*', 'nap', before='refuse')
machine.add_transition('on_wrong_input', '*', 'nap')

@app.route('/{}'.format(bot_token), methods=['POST'])
def respond():

   update = telegram.Update.de_json(request.get_json(force=True), bot_)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id


   text = update.message.text.encode('utf-8').decode()
   text = text.lower()

   # ToDo use regexes below instead of list of words
   #allowed words list = ['pizza', 'пица', 'пиц', 'иц',
   #'ицца', 'цца', 'большая', 'маленькая' ,'мал', 'мале', 'алень', 'да', 'д', 'нет'
   #'не', 'не', 'над', 'пусть' 'н']
   recognition_list = ['пицца', 'pizza', 'большую', 'маленькую','наличкой', 'да', 'нет']

   if text in recognition_list:
       if fs.is_nap():
           if text == "пицца":
               ord.set_id(chat_id)
               fs.new_order(chat_id, msg_id)

       if fs.is_ask_which():
           if text in ["большую", "маленькую"]:
               ord.set_size(text)
               fs.consent(chat_id, msg_id)

       if fs.is_ack():
           if text == "наличкой":
               ord.set_payment_type(text)
               fs.to_bed(ord.size, ord.p_type, chat_id, msg_id)

       if fs.is_half_nap():
           if text == "да":
               ord.throw_to_db()
               fs.sleep(chat_id, msg_id)
               ConversationHandler.END
           
           if text == "нет":
               fs.on_refuse(chat_id, msg_id)
               ConversationHandler.END

   else:
       
       try:
           fs.on_wrong_input()
           text = re.sub(r"\W", "_", text)
           bot_.sendMessage(chat_id=chat_id, text=text + " - Я еще учусь и этого не понимаю. Попробуйте начать словом 'пицца'")
       except Exception:

           bot_.sendMessage(chat_id=chat_id, text="Something happened to me... ask developers",
           reply_to_message_id=msg_id)

   return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
   s = bot_.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=bot_token))
   if s:
       return "webhook ok"
   else:
       return "webhook not ok"

@app.route('/')
def index():
   return 'hi'




if __name__ == '__main__':
   app.run(threaded=True)
