import requests


class Emoji:
    # https://apps.timwhitlock.info/emoji/tables/unicode
    emoji_dict = {
        "default": u'\U0000267F',
        "wheelchair": u'\U0000267F',
        "fire": u'\U0001F525',
        "rocket": u'\U0001F680',
        "chart": u'\U0001F4CA',
        "chartup": u'\U0001F4C8',
        "chartdown": u'\U0001F4C9',
        "heavy_exclamation": u'\U00002757',
        "cross_red": u'\U0000274C',
        "check": u'\U00002705',
        "warning": u'\U000026A0',
        "lightning": u'\U000026A1',
        "arrow_up": u'\U00002B06',
        "arrow_down": u'\U00002B07',
        "money_bag": u'\U0001F4B0',
        "trophy": u'\U0001F3C6',
        "builder": u'\U0001F477',
    }

    def print(self, emoji_name):
        if emoji_name in self.emoji_dict:
            return self.emoji_dict[emoji_name]
        else:
            return self.emoji_dict["default"]


class Telegram:
    api_url = "https://api.telegram.org/"

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message):
        url = self.api_url + 'bot' + self.bot_token + '/sendMessage?chat_id=' + self.chat_id + "&text=" + message
        result = requests.get(url)
        return result


# if __name__ == "__main__":
#     inca = Telegram(Config.BOT_TOKEN, Config.CHAT_ID)
#     test_message = f"Testbot \n{Emoji.print(Emoji, emoji_name='rocket')}"
#     resp = inca.send_message(test_message)
#     print(resp.json())
