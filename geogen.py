import pyroutelib3
import geojson
import json
import math

# configure a routing type 'bus' which is allowed to use all highway types the same
# since the base network has already been cleaned up and contains only ways which are accessible for a bus

_bus_mode = {
  'name': 'bus',
  'weights': {
      'motorway': 0.5,
      'trunk': 0.75,
      'primary': 1.0,
      'secondary': 1.0,
      'tertiary': 1.0,
      'unclassified': 1.0,
      'residential': 1.0,
      'living_street': 1.0,
      'pedestrian': 1.0,
      'footway': 1.0
  },
  'access': ['access', 'walk']
}

# create router object optimized for bus routing network
_router = pyroutelib3.Router(transport=_bus_mode, localfile='data/network.osm.pbf', localfileType='pbf')


# calculate compass direction of two lat lon coordinates
def _bearing(lat1, lon1, lat2, lon2):
    delta_lon = lon2 - lon1
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    compass_brackets = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    compass_lookup = round(bearing / 45)

    return bearing


# calculate a node sequence along a list of GPS coordinates
def node_sequence(*points):

    result = list()

    last_point = points[0]
    for i in range(1, len(points)):

        current_point = points[i]

        start = _router.findNode(last_point[0], last_point[1])
        end = _router.findNode(current_point[0], current_point[1])

        status, lst = _router.doRoute(start, end)

        if status == 'success':
            result += lst

        last_point = current_point

    return result, list(map(_router.nodeLatLon, result))


# generates a GeoJSON file of a list of lat lon coordinates
def create_geojson_file(file_name, lat_lon_list, node_seq=None, router=None):

    features = list()

    line_geometry = geojson.LineString([(e[1], e[0]) for e in lat_lon_list])
    features.append(geojson.Feature(geometry=line_geometry))

    # add points to geojson file if present
    if node_seq is not None and router is not None:
        for node in node_seq:
            point_geometry = geojson.Point((router.rnodes[node][1], router.rnodes[node][0]))
            features.append(geojson.Feature(geometry=point_geometry, properties={'id': node}))

    feature_collection = geojson.FeatureCollection(features)

    with open(file_name, 'w') as f:
        geojson.dump(feature_collection, f)

        f.close()


# generates a sequence file containing a node sequence
def create_sequence_file(file_name, node_seq):

    with open(file_name, 'w') as f:
        for node in node_seq:
            f.write(str(node) + '\n')

        f.close()


def create_routing_network_file(file_name, router):

    routing_network = dict()

    for n, l in router.routing.items():

        current_node = router.rnodes[n]

        if n not in routing_network.keys():
            routing_network[n] = dict()
            routing_network[n]['lat'] = current_node[0]
            routing_network[n]['lon'] = current_node[1]
            routing_network[n]['links'] = list()

        for d, c in l.items():

            destination_node = router.rnodes[d]

            routing_network[n]['links'].append({
                'destination': d,
                'direction': _bearing(current_node[0], current_node[1], destination_node[0], destination_node[1])
            })

    with open(file_name, 'w') as f:
        json.dump(routing_network, f)

        f.close()


if __name__ == '__main__':

    # save routing network for further use
    print('generate routing network')
    create_routing_network_file('output/network.osm.json', _router)
    create_routing_network_file('data/network.osm.json', _router)

    # generate route for Büchenbronn > Pforzheim
    print('generate route for Büchenbronn > Pforzheim')
    route, coord = node_sequence(
        (48.87917449292336, 8.666250334909979),
        (48.889066700003916, 8.694962443144023),
        (48.893077051825045, 8.701193514567818)
    )

    create_geojson_file('output/city.geojson', coord, route, _router)
    create_sequence_file('output/city.seq', route)
    create_sequence_file('data/city.seq', route)

    # generate route for Kapfenhardt > Salmbach
    print('generate route for Kapfenhardt > Salmbach')
    route, coord = node_sequence(
        (48.80895982835148, 8.684386529160776),
        (48.80764396555904, 8.682017588676718),
        (48.80816508587174, 8.645243047580742),
        (48.82234683910327, 8.657529358624494),
        (48.83103294441452, 8.658943637258298)
    )

    create_geojson_file('output/land1.geojson', coord, route, _router)
    create_sequence_file('output/land1.seq', route)
    create_sequence_file('data/land1.seq', route)

    # generate route for Langenbrand > Salmbach
    print('generate route for Langenbrand > Salmbach')
    route, coord = node_sequence(
        (48.80122579013107, 8.634447090041517),
        (48.808163730290104, 8.645044508212116),
        (48.82234683910327, 8.657529358624494),
        (48.83103294441452, 8.658943637258298)
    )

    create_geojson_file('output/land2.geojson', coord, route, _router)
    create_sequence_file('output/land2.seq', route)
    create_sequence_file('data/land2.seq', route)

    # print network information
    print()
    for n, l in _router.routing.items():

        current_node = _router.rnodes[n]

        print(n)
        print('https://maps.google.com/maps?q={0:.10f},{1:.10f}'.format(current_node[0], current_node[1]))

        for d, c in l.items():

            destination_node = _router.rnodes[d]

            print('link {0} > {1}'.format(
                d,
                _bearing(current_node[0], current_node[1], destination_node[0], destination_node[1])
            ))
