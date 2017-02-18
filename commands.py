from config import Config
from db import DB


class Commands:
    @staticmethod
    def add(text, user, user_name, swear_db):
        command_length = len("{} add ".format(Config.AT_BOT))
        text = text[command_length:]
        swearword = text.split('"')[1].strip()
        value = int(text.split('"')[2].strip() or 1)
        if user == "U2G3CA9ND":
            if swearword not in swear_db.data:
                swear_db.data[swearword] = value
                swear_db.write()
                return '"{}" added with the value of {}.'.format(swearword, value), None
            else:
                return '"{}" is already monitored.'.format(swearword), None
        else:
            return "I'm sorry, {}. I can't do that.".format(user_name), None

    @staticmethod
    def error(keywords, user_name=""):
        response = "Avaliable commands are *{}*, and *{}*. Run `{} help` to see how to use them.".format(
            "*, *".join(list(keywords.keys())[:-1]), list(keywords.keys())[-1], Config.AT_BOT)
        return response, "http://i0.kym-cdn.com/photos/images/newsfeed/000/173/576/Wat8.jpg?1315930535"

    @staticmethod
    def help(keywords):
        longest = len(max(keywords.keys(), key=len))
        response = "Available commands are:\n>>>"
        for kw in keywords:
            response += "`{:<{}}` — {}\n".format(kw, longest, keywords[kw])
        return response, None

    @staticmethod
    def highscore(usernames, user_db):
        ordered_keys = sorted(user_db.data, key=user_db.data.get, reverse=True)
        response = "Swear highscore:\n"
        for key in ordered_keys:
            response += "*{}*: {}\n".format(usernames[key], user_db.data[key])
        return response, None

    @staticmethod
    def swears(swear_db):
        ordered_keys = sorted(swear_db.data)
        response = "Registered *swears* are:\n>>> "
        response += ", ".join(["*{}* ({})".format(key, swear_db.data[key]) for key in ordered_keys])
        return response, None

    @staticmethod
    def warning(user_id, user_name, user_db):
        first_name = user_name.split(' ')[0]
        response = ":bangbang: Hey *{}*! (<@{}>) :bangbang:\n".format(first_name, user_id)
        response += "You sweared :zipper_mouth_face: and you should feel bad :point_up:. "
        response += "You have *{}* point(s).".format(user_db.data[user_id])
        return response
