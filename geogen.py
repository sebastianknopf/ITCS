import json

from osmenv.routing import OfflineRouter
from osmenv.geo import GeoJsonFile

# create router object optimized for bus routing network
router = OfflineRouter('data/network.osm.pbf', {
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
        'access': ['access', 'walk', 'psv']
    }
)


# generates a GeoJSON file of a list of lat lon coordinates
def create_geojson_file(filename, lat_lon_list):

    file = GeoJsonFile()
    file.add_line(lat_lon_list)
    file.save(filename)


# generates a sequence file containing a node sequence
def create_sequence_file(file_name, node_seq, length):

    sequence_file_content = {
        'length': length,
        'nodes': node_seq
    }

    with open(file_name, 'w') as f:
        json_content = json.dumps(sequence_file_content)
        f.write(json_content)

        f.close()


if __name__ == '__main__':

    # generate route for Büchenbronn > Pforzheim
    print('generate regular route for Büchenbronn > Pforzheim')
    _, sequence, coord, length = router.find_route(
        (48.87917449292336, 8.666250334909979),
        (48.893077051825045, 8.701193514567818),
        via_list=[
            (48.889066700003916, 8.694962443144023)
        ]
    )

    create_geojson_file('output/city2.geojson', coord)
    create_sequence_file('output/city2.json', sequence, length)

    print('generate deviation routes for Büchenbronn > Pforzheim')
    _, sequence, coord, length = router.find_route(
        (48.884845575, 8.671551539),
        (48.89093284, 8.69518058),
        via_list=[
            (48.88540607, 8.67119330),
            (48.8901226, 8.6790353),
            (48.89160820, 8.68819745),
            (48.890899, 8.692609)
        ]
    )

    create_geojson_file('output/city2_dev1.geojson', coord)
    create_sequence_file('output/city2_dev1.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.88916557, 8.68662533),
        (48.89093284, 8.69518058),
        via_list=[
            (48.888653, 8.680087),
            (48.89160820, 8.68819745),
            (48.890899, 8.692609)
        ]
    )

    create_geojson_file('output/city2_dev2.geojson', coord)
    create_sequence_file('output/city2_dev2.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.88916557, 8.68662533),
        (48.8919824, 8.6959677),
        via_list=[
            (48.888653, 8.680087),
            (48.891160, 8.690216),
            (48.892090, 8.694039)
        ]
    )

    create_geojson_file('output/city2_dev3.geojson', coord)
    create_sequence_file('output/city2_dev3.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.88916557, 8.68662533),
        (48.8919824, 8.6959677),
        via_list=[
            (48.892362, 8.687822)
        ]
    )

    create_geojson_file('output/city2_dev4.geojson', coord)
    create_sequence_file('output/city2_dev4.json', sequence, length)

    print()

    # generate route for Kapfenhardt > Salmbach
    print('generate regular route for Kapfenhardt > Salmbach')
    _, sequence, coord, length = router.find_route(
        (48.80895982835148, 8.684386529160776),
        (48.83103294441452, 8.658943637258298),
        via_list=[
            (48.80764396555904, 8.682017588676718),
            (48.80816508587174, 8.645243047580742),
            (48.82234683910327, 8.657529358624494)
        ]
    )

    create_geojson_file('output/land744.geojson', coord)
    create_sequence_file('output/land744.json', sequence, length)

    print('generate deviation routes for Kapfenhardt > Salmbach')
    _, sequence, coord, length = router.find_route(
        (48.807953675, 8.645416687),
        (48.82241938, 8.65755125),
        via_list=[
            (48.807953420, 8.645416422)
        ],
        not_via_list=[
            (48.817129, 8.649925)
        ]
    )

    create_geojson_file('output/land744_dev1.geojson', coord)
    create_sequence_file('output/land744_dev1.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.8089475, 8.6843423),
        (48.82241938, 8.65755125),
        via_list=[
            (48.8111710, 8.6850683)
        ],
        not_via_list=[
            (48.817129, 8.649925)
        ]
    )

    create_geojson_file('output/land744_dev2.geojson', coord)
    create_sequence_file('output/land744_dev2.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.8089475, 8.6843423),
        (48.82241938, 8.65755125),
        via_list=[
            (48.8320338, 8.6738655)
        ],
        not_via_list=[
            (48.817129, 8.649925)
        ]
    )

    create_geojson_file('output/land744_dev3.geojson', coord)
    create_sequence_file('output/land744_dev3.json', sequence, length)

    print()

    # generate route for Langenbrand > Salmbach
    print('generate regular route for Langenbrand > Salmbach')
    _, sequence, coord, length = router.find_route(
        (48.80122579013107, 8.634447090041517),
        (48.83103294441452, 8.658943637258298),
        via_list=[
            (48.808163730290104, 8.645044508212116),
            (48.82234683910327, 8.657529358624494),
        ]
    )

    create_geojson_file('output/land743.geojson', coord)
    create_sequence_file('output/land743.json', sequence, length)

    print('generate deviation routes for Langenbrand > Salmbach')
    _, sequence, coord, length = router.find_route(
        (48.8080498, 8.6447907),
        (48.82241938, 8.65755125),
        not_via_list=[
            (48.817129, 8.649925)
        ]
    )

    create_geojson_file('output/land743_dev1.geojson', coord)
    create_sequence_file('output/land743_dev1.json', sequence, length)

    _, sequence, coord, length =  router.find_route(
        (48.8080498, 8.6447907),
        (48.82241938, 8.65755125),
        via_list=[
            (48.832037, 8.674020)
        ],
        not_via_list=[
            (48.817129, 8.649925)
        ]
    )

    create_geojson_file('output/land743_dev2.geojson', coord)
    create_sequence_file('output/land743_dev2.json', sequence, length)

    print()

    # generate route for Pforzheim > Neuenbürg
    print('generate regular route for Pforzheim > Neuenbürg')
    _, sequence, coord, length = router.find_route(
        (48.8891678, 8.6660846),
        (48.859522, 8.609634),
        via_list=[
            (48.8770980, 8.6447771),
            (48.8741511, 8.6419259),
            (48.8729455, 8.6428635),
            (48.8716730, 8.6427678),
            (48.8701613, 8.6357738),
            (48.8702570, 8.6265982)
        ]
    )

    create_geojson_file('output/village715.geojson', coord)
    create_sequence_file('output/village715.json', sequence, length)

    print('generate deviation routes for Pforzheim > Neuenbürg')
    _, sequence, coord, length = router.find_route(
        (48.8795760, 8.6489128),
        (48.87120777, 8.64003084),
        via_list=[
            (48.8733121, 8.6440099),
            (48.8704752, 8.6416179)
        ]
    )

    create_geojson_file('output/village715_dev1.geojson', coord)
    create_sequence_file('output/village715_dev1.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.8795760, 8.6489128),
        (48.8705015, 8.6257640),
        via_list=[
            (48.8733121, 8.6440099),
            (48.8704752, 8.6416179),
            (48.873179, 8.636156),
            (48.8753991, 8.6294823)
        ]
    )

    create_geojson_file('output/village715_dev2.geojson', coord)
    create_sequence_file('output/village715_dev2.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.8705661, 8.6364884),
        (48.8705015, 8.6257640),
        via_list=[
            (48.873179, 8.636156),
            (48.8753991, 8.6294823)
        ]
    )

    create_geojson_file('output/village715_dev3.geojson', coord)
    create_sequence_file('output/village715_dev3.json', sequence, length)

    _, sequence, coord, length = router.find_route(
        (48.8877129, 8.6643343),
        (48.8705015, 8.6257640),
        via_list=[
            (48.884369, 8.640431)
        ]
    )

    create_geojson_file('output/village715_dev4.geojson', coord)
    create_sequence_file('output/village715_dev4.json', sequence, length)

    # create points of osm network file
    geojson = GeoJsonFile()

    for n, c in router._router.rnodes.items():
        geojson.add_point(c, props={'id': n})

    geojson.save('output/osmpoints.geojson')

