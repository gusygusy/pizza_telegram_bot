import requests

import pytest

bot_token = "5075257732:AAG84yGq1sEElKt7jOc58WUXih8Mdf4Zqr4"
bot_user_name = "pizza_qwint_bot"
URL = "http://congadance.pythonanywhere.com"
res = requests.get("https://api.telegram.org/bot5075257732:AAG84yGq1sEElKt7jOc58WUXih8Mdf4Zqr4/"
                   "deleteWebhook")
res_ = requests.get("https://api.telegram.org/bot5075257732:AAG84yGq1sEElKt7jOc58WUXih8Mdf4Zqr4/"
                    "getUpdates")
bot_chatID = res_.json()['chat']['id']


def telegram_bot_dialog(message):
    for i in message:
        ...  # need to handle these properly
    text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' +\
               bot_chatID + '&parse_mode=Markdown&text=' + message

    response = requests.get(text)

    return response.json()

test_list = ['utterance_1', 'utterance_2', 'utterance_3',]


def telegram_bot_dialog_test(foo, test_list):

    assert foo(test_list) == 'SomeValue'