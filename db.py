class DB:
    def __init__(self, filename):
        self.filename = filename
        self.data = dict()
        self.read()

    def read(self):
        self.data = dict()
        with open(self.filename) as input_db:
            for line in input_db:
                key = line.split(',')[0].strip()
                value = int(line.split(',')[1].strip())
                if key not in self.data:
                    self.data[key] = value

    def write(self):
        with open(self.filename, 'w') as db_file:
            for key in self.data:
                db_file.write("{},{}\n".format(key, self.data[key]))
