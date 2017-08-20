import collections
import six


class StreamHandler(object):

    def __init__(self):
        self.v2g = {}
        self.g2ip = collections.defaultdict(set)
        self.g2n = collections.defaultdict(set)
        self.gcounter = 0

    def serialize_g2n(self, stream):
        for group, names in six.iteritems(self.g2n):
            for name in names:
                stream.write("{0}\t{1}\n".format(name, group))

    def edge_stream(self, stream):
        for line in stream:
            line_array = line.split()
            if len(line_array) < 2:
                raise ValueError("Incorrect line format: {}".format(line))
            name, ips = line_array[0], line_array[1:]
            for ip in ips:
                yield (name, ip)

    def handle_stream(self, stream):

        for name, ip in self.edge_stream(stream):
            # print("===")
            # print("name:             {}".format(name))
            # print("ip:               {}".format(ip))
            # print("BEFORE v2g:       {}".format(self.v2g))
            # print("BEFORE g2n:       {}".format(self.g2n))
            # print("BEFORE g2ip:      {}".format(self.g2ip))

            name_group = self.v2g.get(name)
            ip_group = self.v2g.get(ip)

            if name_group is None and ip_group is None:
                # print("edge is dis-jointed. gcounter: {}".format(
                #     self.gcounter))
                self.v2g[name] = self.gcounter
                self.v2g[ip] = self.gcounter
                self.g2ip[self.gcounter].add(ip)
                self.g2n[self.gcounter].add(name)
                self.gcounter += 1

            elif name_group is None and ip_group is not None:
                # print("edge is joined to a group {0} via ip: {1}".format(
                #     ip_group, ip))
                self.v2g[name] = ip_group
                self.g2n[ip_group].add(name)

            elif name_group is not None and ip_group is None:
                # print("edge is joined to a group {0} via name: {1}".format(
                #     name_group, name))
                self.v2g[ip] = name_group
                self.g2ip[name_group].add(ip)

            else:
                if name_group != ip_group:
                    # print("edge is joined to two different groups")
                    # print("name_group {0} via name {1}".format(
                    #     name_group, name))
                    # print("ip_group {0} via ip {1}".format(ip_group, ip))

                    # if an edge is joined to two different groups
                    # these groups must be merged
                    # we merge smaller group into bigger one
                    # because merge is O(n), where n is the number of elements
                    # in the group which is merged

                    name_size = len(self.g2n[name_group]) + len(self.g2ip[name_group])
                    ip_size = len(self.g2n[ip_group]) + len(self.g2ip[ip_group])

                    if name_size >= ip_size:
                        bigger = name_group
                        smaller = ip_group
                    else:
                        bigger = ip_group
                        smaller = name_group

                    _names = self.g2n[smaller]
                    for _name in _names:
                        self.v2g[_name] = bigger
                        self.g2n[bigger].add(_name)
                    self.g2n.pop(smaller)

                    _ips = self.g2ip[smaller]
                    for _ip in _ips:
                        self.v2g[_ip] = bigger
                        self.g2ip[bigger].add(_ip)
                    self.g2ip.pop(smaller)

            # print("AFTER v2g:        {}".format(self.v2g))
            # print("AFTER g2n:        {}".format(self.g2n))
            # print("AFTER g2ip:       {}".format(self.g2ip))
