import osmium
import math

from dataclasses import dataclass


def _direction(lat1, lon1, lat2, lon2):
    delta_lon = lon2 - lon1
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    compass_brackets = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    compass_lookup = round(bearing / 45)

    return compass_brackets[compass_lookup]


class OSMNetworkHandler(osmium.SimpleHandler):

    def __init__(self):
        super(OSMNetworkHandler, self).__init__()

        self._wkb_factory = osmium.geom.WKBFactory()

        self.nodes = dict()

    def way(self, w):

        # load only ways which are connected by a node
        if len(w.nodes) > 0:

            way_id = int(w.id)

            for n in w.nodes:

                node_ref = int(n.ref)
                if node_ref in self.nodes.keys():
                    self.nodes.get(node_ref).ways.append(way_id)
                else:
                    self.nodes[node_ref] = Node(node_ref, n.lat, n.lon, [])
                    self.nodes.get(node_ref).ways.append(way_id)

    def generate_nodes(self):

        # remove all nodes NOT representing a INTERSECTION between AT LEAST 2 ways
        key_list = list()
        for n in self.nodes.keys():
            if len(self.nodes.get(n).ways) < 2:
                key_list.append(n)

        for dk in key_list:
            self.nodes.pop(dk, None)

        # iterate over all intersection nodes to find links between other nodes
        data = dict()
        for node_id in self.nodes.keys():

            # get reference to current node
            current_node_obj = self.nodes.get(node_id)

            # add key entry for this node
            links = list()

            # iterate all ways connected to this node to find other nodes
            for way_id in self.nodes.get(node_id).ways:

                node_ids = [k for k, n in
                            self.nodes.items()
                            if way_id in n.ways
                            and n.id != node_id]

                if len(node_ids) > 0:

                    for destination_node_id in node_ids:

                        destination_node_obj = self.nodes.get(destination_node_id)
                        direction = _direction(
                            current_node_obj.lat,
                            current_node_obj.lon,
                            destination_node_obj.lat,
                            destination_node_obj.lon
                        )

                        # add the link between two nodes including its direction for routing
                        links.append(Way(way_id, direction, destination_node_id))

                    # add node to network data
                    data[node_id] = Node(node_id, current_node_obj.lat, current_node_obj.lon, links)

        return data


@dataclass
class Way:
    id: int
    direction: str
    destination: int


@dataclass
class Node:
    id: int
    lat: float
    lon: float
    ways: list


if __name__ == '__main__':
    osm = OSMNetworkHandler()
    osm.apply_file('../data/network.osm.pbf', locations=True)
    nodes = osm.generate_nodes()

    print('found {0:} nodes'.format(len(nodes)))
    print()

    for i, node in nodes.items():
        print(node.id)
        print('https://maps.google.com/maps?q={0:.10f},{1:.10f}'.format(node.lat, node.lon))

        for way in node.ways:
            print(way)

        print()
