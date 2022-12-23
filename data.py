def _load_trip_ways(data_file):
    # read file line by line and pass ways as ordered in file
    with open(data_file) as file:
        ways = [line.rstrip() for line in file]
        return ways


trip743h = {
    'id': '743-H',
    'ways': _load_trip_ways('data/trip743h.txt')
}

trip744h = {
    'id': '744-H',
    'ways': _load_trip_ways('data/trip744h.txt')
}

trip2h = {
    'id': '2-H',
    'ways': _load_trip_ways('data/trip2h.txt')
}
