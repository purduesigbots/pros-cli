
def adr_to_str(address):
    """
    Converts a well-formed bytearray address (i.e. one with a checksum) to a string
    :param address:
    :return:
    """
    return '0x{}({:02X})'.format(''.join('{:02X}'.format(x) for x in address[:-1]), address[-1])


def bytes_to_str(arr):
    if isinstance(arr, str):
        arr = bytes(arr)
    if hasattr(arr, '__iter__'):
        return ''.join('{:02X} '.format(x) for x in arr)
    else:  # actually just a single byte
        return '{:02X}'.format(arr)
