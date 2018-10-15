class ConnectionRefusedException(IOError):
    def __init__(self, port_name: str, reason: Exception):
        self.__cause__ = reason
        self.port_name = port_name

    def __str__(self):
        return f"could not open port '{self.port_name}'. Try closing any other VEX IDEs such as ROBOTC, VCS, or " \
               f"firmware utilities; moving to a different USB port; or restarting the device."
