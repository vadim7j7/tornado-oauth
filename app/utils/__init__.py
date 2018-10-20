import datetime


def compact_result(data: list) -> list:
    buf = []

    for item in data:
        item = dict(item)
        keys = item.keys()
        for key in keys:
            if type(item[key]) is datetime.datetime:
                item[key] = str(item[key])

        buf.append(item)

    return buf
