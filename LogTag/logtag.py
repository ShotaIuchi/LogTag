import argparse
import json
import os
import sys


def all_file_join(file_list: list) -> list:
    all_file = []
    for file in file_list:
        with open(file, 'r') as f:
            all_file += [line.rstrip() for line in f]
    return all_file


def load_json(file: str) -> dict:
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'Error: File not found: {file}')
        sys.exit(1)
    except json.JSONDecodeError:
        print(f'Error: Invalid JSON file: {file}')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='LogTag adds tags to log messages.')
    parser.add_argument('-f', '--file', type=str, nargs='+', help='Files to add tags.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-o', '--only', action='store_true', help='Display only tagged log messages.')

    args = parser.parse_args()

    if args.file:
        all_file = all_file_join(args.file)

        if args.sort:
            all_file = sorted(all_file)

    cwd = os.getcwd()
    pwd = os.path.dirname(os.path.abspath(__file__))

    cfg = load_json(os.path.join(cwd, '.logtag', 'config.json'))
    tag = load_json(os.path.join(cwd, '.logtag', 'logtag.tag.json'))
    filter = load_json(os.path.join(cwd, '.logtag', 'logtag.filter.json'))

    space = cfg['space']

    for line in all_file:
        msg = ''
        for key, value in tag.items():
            if key in line:
                msg = value
                if args.only:
                    print(f'{msg:<{space}}{line}')
                break

        if args.only:
            continue

        if len(filter['display']) > 0:
            for key in filter['display']:
                if key in line:
                    print(f'{msg:<{space}}{line}')
                    break
        else:
            print(f'{msg:<{space}}{line}')


if __name__ == '__main__':
    main()
