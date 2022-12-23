import osmium
import shapely.wkb


class OSMNetworkHandler(osmium.SimpleHandler):

    def __init__(self):
        super(OSMNetworkHandler, self).__init__()

        self.wkb_factory = osmium.geom.WKBFactory()

        self.ways = dict()
        self.nodes = dict()

    def way(self, w):
        try:
            wkb = self.wkb_factory.create_linestring(w)
            line = shapely.wkb.loads(wkb, hex=True)

            self.ways[w.id] = line

        except Exception:
            pass

        for n in w.nodes:
            if n.ref in self.nodes:
                self.nodes.get(n.ref).append(w.id)
            else:
                self.nodes[n.ref] = list()
                self.nodes.get(n.ref).append(w.id)

    def generate_network(self):

        key_list = list()
        for n in self.nodes.keys():
            if len(self.nodes.get(n)) < 2:
                key_list.append(n)

        for dk in key_list:
            self.nodes.pop(dk, None)

        links = dict()
        for n in self.nodes.keys():
            for w in self.nodes.get(n):

                remainder = self.nodes.get(n)[:]
                remainder.remove(w)

                if w in links:
                    links[w] = links[w] + remainder
                else:
                    links[w] = remainder

        return self.ways, links


if __name__ == '__main__':

    osm = OSMNetworkHandler()
    osm.apply_file('../data/network.osm.pbf', locations=True)
    ways, links = osm.generate_network()

    print(ways)
    print(links)
