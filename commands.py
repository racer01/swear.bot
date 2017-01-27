class Commands:
    @staticmethod
    def error(keywords):
        response = "I'm afraid I can't let you do that. "
        response += "Avaliable commands are *{}*".format("*, *".join(keywords.keys()))
        return response

    @staticmethod
    def help(keywords):
        response = "Available commands are "
        return response

    @staticmethod
    def highscore(users, user_db):
        ordered_keys = sorted(user_db, key=user_db.get, reverse=True)
        response = "Swear highscore:\n"
        for key in ordered_keys:
            for user in users:
                if user["id"] == key:
                    response += "*{}*: {}\n".format(user["real_name"], user_db[key])
                    break
        return response

    @staticmethod
    def swears(swear_db):
        ordered_keys = sorted(swear_db)
        response = "Registered *swears* are:\n>>> "
        response += ", ".join(["*{}* ({})".format(key, swear_db[key]) for key in ordered_keys])
        return response

    @staticmethod
    def warning(user, users, user_db):
        first_name = ([u["real_name"] for u in users if u["id"] == user][0]).split(' ')[0]
        response = ":bangbang: Hey *{}*! (<@{}>) :bangbang:\n".format(first_name, user)
        response += "You sweared :zipper_mouth_face: and you should feel bad :point_up:. "
        response += "You have *{}* point(s).".format(user_db[user])
        return response
