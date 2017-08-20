import unittest2

import mock

from ..stream import StreamHandler


class TestStreamHandler(unittest2.TestCase):
    def test_add_disjoined_edge(self):
        stream = [
            "name1 ip1",
            "name2 ip2"
        ]
        ref_g2n = {
            0: set(["name1"]),
            1: set(["name2"])
        }
        ref_g2ip = {
            0: set(["ip1"]),
            1: set(["ip2"])
        }
        ref_v2g = {
            "name1": 0,
            "ip1": 0,
            "name2": 1,
            "ip2": 1
        }
        sh = StreamHandler()
        sh.handle_stream(stream)
        self.assertDictEqual(ref_g2n, sh.g2n)
        self.assertDictEqual(ref_g2ip, sh.g2ip)
        self.assertDictEqual(ref_v2g, sh.v2g)

    def test_add_name_joined_edge(self):
        stream = [
            "name1 ip1 ip2",
            "name2 ip3",
            "name1 ip4"
        ]
        ref_g2n = {
            0: set(["name1"]),
            1: set(["name2"])
        }
        ref_g2ip = {
            0: set(["ip1", "ip2", "ip4"]),
            1: set(["ip3"])
        }
        ref_v2g = {
            "name1": 0,
            "ip1": 0,
            "ip2": 0,
            "name2": 1,
            "ip3": 1,
            "ip4": 0
        }
        sh = StreamHandler()
        sh.handle_stream(stream)
        self.assertDictEqual(ref_g2n, sh.g2n)
        self.assertDictEqual(ref_g2ip, sh.g2ip)
        self.assertDictEqual(ref_v2g, sh.v2g)

    def test_add_ip_joined_edge(self):
        stream = [
            "name1 ip1 ip2",
            "name2 ip3",
            "name3 ip1"
        ]
        ref_g2n = {
            0: set(["name1", "name3"]),
            1: set(["name2"])
        }
        ref_g2ip = {
            0: set(["ip1", "ip2"]),
            1: set(["ip3"])
        }
        ref_v2g = {
            "name1": 0,
            "ip1": 0,
            "ip2": 0,
            "name2": 1,
            "ip3": 1,
            "name3": 0
        }
        sh = StreamHandler()
        sh.handle_stream(stream)
        self.assertDictEqual(ref_g2n, sh.g2n)
        self.assertDictEqual(ref_g2ip, sh.g2ip)
        self.assertDictEqual(ref_v2g, sh.v2g)

    def test_add_name_ip_joined_edge(self):
        stream = [
            "name1 ip1",
            "name2 ip2",
            "name3 ip3",
            "name1 ip2",
        ]
        ref_g2n = {
            0: set(["name1", "name2"]),
            2: set(["name3"]),
        }
        ref_g2ip = {
            0: set(["ip1", "ip2"]),
            2: set(["ip3"]),
        }
        ref_v2g = {
            "name1": 0,
            "ip1": 0,
            "name2": 0,
            "ip2": 0,
            "name3": 2,
            "ip3": 2,
        }
        sh = StreamHandler()
        sh.handle_stream(stream)
        self.assertDictEqual(ref_g2n, sh.g2n)
        self.assertDictEqual(ref_g2ip, sh.g2ip)
        self.assertDictEqual(ref_v2g, sh.v2g)

    def test_edge_generator(self):
        stream = [
            "name1 ip1 ip2",
            "name2 ip3 ip4 ip2",
            "name1 ip5"
        ]
        ref_edges = [
            ("name1", "ip1"),
            ("name1", "ip2"),
            ("name2", "ip3"),
            ("name2", "ip4"),
            ("name2", "ip2"),
            ("name1", "ip5"),
        ]
        edges = []
        sh = StreamHandler()
        for name, ip in sh.edge_stream(stream):
            edges.append((name, ip))
        self.assertListEqual(ref_edges, edges)

    def test_serialize_g2n(self):
        sh = StreamHandler()
        sh.g2n = {
            0: set(["name1", "name2"]),
            1: set(["name3"]),
            100: set(["name4"])
        }
        stream = mock.Mock()
        ref_stream_calls = [
            mock.call("name1\t0\n"),
            mock.call("name2\t0\n"),
            mock.call("name3\t1\n"),
            mock.call("name4\t100\n"),
        ]
        sh.serialize_g2n(stream)
        actual_stream_calls = stream.write.call_args_list
        for c in ref_stream_calls:
            assert c in actual_stream_calls
