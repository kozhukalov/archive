import argparse
import sys

from .stream import StreamHandler


class Stream(object):
    def __init__(self, stream_name, stream_type="r"):
        self.stream_name = stream_name
        self.stream_type = stream_type
        self.need_close = False

    def __enter__(self):
        if self.stream_name == "-":
            if self.stream_type == "r":
                self.stream = sys.stdin
            else:
                self.stream = sys.stdout
        else:
            self.stream = open(self.stream_name, self.stream_type)
            self.need_close = True
        return self.stream

    def __exit__(self, type, value, traceback):
        if self.need_close:
            self.stream.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="-", required=False,
                        help="Input file. By default, stdin is used.")
    parser.add_argument("--output", default="-", required=False,
                        help="Output file. By default, stdout is used.")

    args, other = parser.parse_known_args()

    sh = StreamHandler()

    with Stream(args.input) as f:
        sh.handle_stream(f)

    with Stream(args.output, "w") as f:
        sh.serialize_g2n(f)


if __name__ == "__main__":
    main()
