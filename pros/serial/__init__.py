def bytes_to_str(arr):
    if isinstance(arr, str):
        arr = bytes(arr)
    if hasattr(arr, '__iter__'):
        return ''.join('{:02X} '.format(x) for x in arr).strip()
    else:  # actually just a single byte
        return '0x{:02X}'.format(arr)
