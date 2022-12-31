import pyroutelib3


class OfflineRouter:

    def __init__(self, osm_filename, router_type):

        self._router = pyroutelib3.Router(transport=router_type, localfile=osm_filename, localfileType='pbf')

    def _length(self, node_sequence):

        length = 0.0
        for i in range(1, len(node_sequence)):
            pos1 = self._router.rnodes[node_sequence[i - 1]]
            pos2 = self._router.rnodes[node_sequence[i]]

            length += self._router.distance(pos1, pos2)

        return length

    def _standard_location(self, location):

        if type(location) is tuple and len(location) == 2:
            return self._router.findNode(location[0], location[1])
        elif type(location) is int:
            return location
        else:
            raise RuntimeError('invalid location, expected type int or tuple(2)')

    def route_length(self, locations):

        # transform locations into node sequence
        node_sequence = [self._standard_location(l) for l in locations]

        return self._length(node_sequence)

    def route_contains_point(self, locations, point):

        # transform point to closest node ID
        node = self._standard_location(point)

        # if the closest node is more than 130m away, ignore it - it can't be on route
        # this high distance is needed since there are some ways which have points with a distance greater than 200m
        distance = self._router.distance(
            (self._router.rnodes[node][0], self._router.rnodes[node][1]),
            (point[0], point[1])
        )

        if distance > 0.130:
            return False

        # transform location list into node sequence
        node_sequence = [self._standard_location(l) for l in locations]

        return node in node_sequence

    def find_route(self, start, destination, via_list=None, not_via_list=None):

        # standardize start and destination
        start = self._standard_location(start)
        destination = self._standard_location(destination)

        # temporary save loaded routing network
        # remove not-via items out of routing network
        _routing_network = self._router.routing.copy()
        if not_via_list is not None:
            for not_via in not_via_list:

                not_via = self._standard_location(not_via)
                if not_via in self._router.routing.keys():
                    self._router.routing.pop(not_via, None)

        # define result containers
        node_sequence = list()
        status = 'success'

        # if there's a list of via points, calculate route step wise in order to match the via points
        last_node = start
        if via_list is not None:
            for via in via_list:

                via = self._standard_location(via)

                code, nodes = self._router.doRoute(last_node, via)
                if code == 'success':
                    node_sequence += nodes
                elif code != 'success' and status == 'success':
                    status = code

                last_node = via

        # find route to last step
        code, nodes = self._router.doRoute(last_node, destination)
        if code == 'success':
            node_sequence += nodes
        elif code != 'success' and status == 'success':
            status = code

        # reset routing network back to what was loaded originally
        self._router.routing = _routing_network

        # generate return values
        lat_lon_list = list(map(self._router.nodeLatLon, node_sequence))
        length = self._length(node_sequence)

        return status, node_sequence, lat_lon_list, length
