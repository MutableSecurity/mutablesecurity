import re


def parse_connection_string(connection_string):
    username = None
    hostname = None
    port = None

    match = re.match(
        "(.*)@(.*):((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))",
        connection_string,
    )
    if match:
        username, hostname, port, *_ = match.groups()

        return (username, hostname, int(port))
    else:
        return None
