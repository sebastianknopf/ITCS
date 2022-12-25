

def _load_trip_ways(data_file):
    # read file line by line and pass ways as ordered in file
    with open(data_file) as file:
        ways = [int(line.rstrip()) for line in file]
        return ways


_trip743h = {
    'id': '743-H',
    'ways': _load_trip_ways('data/trip743h.txt')
}

_trip744h = {
    'id': '744-H',
    'ways': _load_trip_ways('data/trip744h.txt')
}

_trip2h = {
    'id': '2-H',
    'ways': _load_trip_ways('data/trip2h.txt')
}

trips = [_trip2h, _trip743h, _trip744h]
