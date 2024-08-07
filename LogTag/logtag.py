import argparse
import json
import os
import sys
from tempfile import TemporaryFile
from wcwidth import wcswidth


DOTDIR = '.logtag'

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


# join all files
def all_file_join(file_list: list) -> list:

    all_line = []

    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = [line.rstrip() for line in lines]
            all_line += lines

    return all_line


# read config files
def read_dotfile(arg_directory: str, file: str) -> dict:
    # Priority: arg_directory > HOME > CWD > PWD
    target_file = ''
    if os.path.isfile(os.path.join(arg_directory, file)):
        target_file = os.path.join(arg_directory, file)
    elif os.path.isfile(os.path.join(HOME, DOTDIR, file)):
        target_file = os.path.join(HOME, DOTDIR, file)
    elif os.path.isfile(os.path.join(CWD, DOTDIR, file)):
        target_file = os.path.join(CWD, DOTDIR, file)
    elif os.path.isfile(os.path.join(PWD, DOTDIR, file)):
        target_file = os.path.join(PWD, DOTDIR, file)
    else:
        print(f'Error: File not found: {file}')
        sys.exit(1)

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
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
    parser.add_argument('-o', '--out', type=str, help='Output file.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-u', '--uniq', action='store_true', help='Remove duplicate log messages.')
    parser.add_argument('--config', type=str, help='Config file.')

    args = parser.parse_args()

    # read config files
    cfg = read_dotfile(args.config, 'config.json')
    tag = read_dotfile(args.config, 'logtag.tag.json')
    filter = read_dotfile(args.config, 'logtag.filter.json')

    space = cfg['space']
    filter_display = filter['display']

    # read all log messages
    if args.file:
        all_file = all_file_join(args.file)

        # sort log messages
        if args.sort:
            all_file = sorted(all_file)
    else:
        print('Error: No input files.')
        sys.exit(1)

    # convert log messages
    with TemporaryFile('w+', encoding='utf-8') as tp:
        # write to tempolary file
        def print_tp(msg, line):
            calc_space = space - (wcswidth(msg) - len(msg))
            return tp.write(f'{msg:<{calc_space}}{line}\n')

        # convert log messages
        for line in all_file:
            msg = ''
            for key, value in tag.items():
                if key in line:
                    msg = value
                    if args.uniq:
                        print_tp(msg, line)
                    break

            # remove duplicate log messages
            if args.uniq:
                continue

            if len(filter_display) > 0:
                # filter log messages
                for key in filter_display:
                    if key in line:
                        print_tp(msg, line)
                        break
            else:
                print_tp(msg, line)

        # read tempolary file
        tp.seek(0)
        tf = tp.read()

        # print converted log messages to stdout
        print(tf)

        # write converted log messages to output file
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(tf)


if __name__ == '__main__':
    main()
