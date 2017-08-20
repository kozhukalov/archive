import argparse
from functools import partial
import itertools
import random
import string


octs = [random.randrange(1, 255) for _ in range(4)]


def gen_ip():
    return ".".join(str(random.choice(octs)) for _ in range(4))


def gen_domain():
    return ".".join(
        "".join(
            random.choice(string.ascii_lowercase)
            for _ in range(random.randrange(2, 6))
        ) for _ in range(random.randrange(2, 4))
    )


def gen_bullshit():
    while True:
        yield gen_domain() + "\t" + "\t".join(
            gen_ip() for _ in range(random.randrange(1, 4))
        )


def check_stop(count, item, maxcount):
    if count == maxcount:
        raise StopIteration()
    return item


def gen_stream(maxcount=100):
    for item in itertools.starmap(
        partial(check_stop, maxcount=maxcount),
        enumerate(gen_bullshit())
    ):
        yield item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", default=100, type=int, required=False,
                        help="Number of lines to generate.")

    args, other = parser.parse_known_args()
    for line in gen_stream(args.num):
        print(line)


if __name__ == "__main__":
    main()
