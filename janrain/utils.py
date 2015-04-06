def utf8_encode(s):
    try:
        if isinstance(s, unicode):
            return s.encode('utf-8')
        else:
            return s
    except NameError as err:
        if isinstance(s, str):
            return s.encode()
        else:
            return s
