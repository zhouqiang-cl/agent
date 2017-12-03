# -*- coding: utf-8 -*-
def to_byte(data):
    data = data.lower()
    if data.endswith("b"):
        data = data[:-1]
    unit = {
        "b":1,
        "k":1024,
        "m":1024*1024,
        "g":1024*1024*1024
    }
    last_char = data[-1]
    if last_char not in unit.keys():
        data = data + "b"
        last_char = "b"
    rate = int(data[:-1])*unit[last_char]
    return rate

if __name__ == "__main__":
    print to_byte("1b")
    print to_byte("1K")
    print to_byte("1M")
    print to_byte("1g")