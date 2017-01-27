import os


class Command:
    # swear.bot's ID as an environment variable
    BOT_ID = os.environ.get("SLACK_BOT_ID")
    # constants
    AT_BOT = "<@" + BOT_ID + ">"

    def __init__(self, name, command, description, regex_name=None):
        self.name = name
        self.command = command
        self.regex_name = regex_name or self.command_regexify
        self.description = description

    @property
    def command_regexify(self):
        return "{} {}".format(self.AT_BOT, self.name)
