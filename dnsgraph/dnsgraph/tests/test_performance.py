import time

import unittest2

from ..stream import StreamHandler
from .gen import gen_stream


class TestPerformance(unittest2.TestCase):

    @unittest2.skip
    def test_performance(self):

        sh = StreamHandler()
        stream_10_5 = gen_stream(10 ** 5)
        begin_10_5 = time.time()
        sh.handle_stream(stream_10_5)
        time_10_5 = time.time() - begin_10_5

        sh = StreamHandler()
        stream_10_6 = gen_stream(10 ** 6)
        begin_10_6 = time.time()
        sh.handle_stream(stream_10_6)
        time_10_6 = time.time() - begin_10_6

        assert (time_10_6 / time_10_5) < 40
