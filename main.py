import sys
from parse import parse


def main(*args):
    start_url = args[0].strip()
    if not start_url.startswith(("http://", "https://")):
        start_url = "https://" + start_url
    result = parse(start_url)
    print(result)


if __name__ == "__main__":
    main(*sys.argv[1:])
