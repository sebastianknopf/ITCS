import geojson


class GeoJsonFile:

    def __init__(self):

        self._features = list()

    def add_line(self, lat_lon_list, props=None):

        line_geometry = geojson.LineString([(e[1], e[0]) for e in lat_lon_list])
        self._features.append(geojson.Feature(geometry=line_geometry, properties=props))

    def add_point(self, lat_lon, props=None):

        point_geometry = geojson.Point((lat_lon[1], lat_lon[0]))
        self._features.append(geojson.Feature(geometry=point_geometry, properties=props))

    def save(self, filename):

        feature_collection = geojson.FeatureCollection(self._features)

        with open(filename, 'w') as f:
            geojson.dump(feature_collection, f)

            f.close()
