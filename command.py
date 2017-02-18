from config import Config


class Command:

    def __init__(self, name, command, description, regex_name=None):
        self.name = name
        self.command = command
        self.description = description
        self.regex_name = regex_name or self._regexified_name

    @property
    def _regexified_name(self):
        return "{} {}".format(Config.AT_BOT, self.name)
