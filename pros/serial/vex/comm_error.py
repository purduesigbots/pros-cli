class VEXCommError(Exception):
    def __init__(self, message, msg):
        self.message = message
        self.msg = msg

    def __str__(self):
        return "{}\n{}".format(self.message, self.msg)
