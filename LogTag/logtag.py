import argparse
import glob
import json
import os
import re
import sys
from tempfile import TemporaryFile
from wcwidth import wcswidth


DOTDIR = '.logtag'

DOT_CONFIG = 'config.json'
DOT_TAG = r'^([0-9]+-.*-tag|[0-9]+-tag|tag)\.json$'
DOT_FILTER = r'^([0-9]+-.*-filter|[0-9]+-filter|filter)\.json$'

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


# join all files
def all_file_join(pattern_list: list) -> list:
    all_line = []
    for pattern in pattern_list:
        file_list = glob.glob(pattern)
        for file in file_list:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                lines = [line.rstrip() for line in lines]
                all_line += lines

    return all_line


# load config file
def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


# merge config files
def merge_configs(configs):
    final_config = {}
    for config in configs:
        final_config.update(config)
    return final_config


# read config files
def read_dotfiles(directory: str, pattern: str) -> dict:
    # Priority: Lexicographically ordered
    configs = []
    regex = re.compile(pattern)
    if os.path.exists(directory):
        files = os.listdir(directory)
        files = sorted(files)
        for filename in files:
            if regex.match(filename):
                file_path = os.path.join(directory, filename)
                configs.append(load_config(file_path))
    return merge_configs(configs)


# read config files
def read_dotfile(arg_directory: str, file: str) -> dict:
    # Priority: arg_directory > CWD > HOME > PWD
    configs = []
    if arg_directory:
        configs.append(read_dotfiles(arg_directory, file))
    configs.append(read_dotfiles(os.path.join(CWD, DOTDIR), file))
    configs.append(read_dotfiles(os.path.join(HOME, DOTDIR), file))
    configs.append(read_dotfiles(os.path.join(PWD, DOTDIR), file))
    return merge_configs(configs)


def main():
    parser = argparse.ArgumentParser(description='LogTag adds tags to log messages.')
    parser.add_argument('-f', '--file', type=str, nargs='+', help='Files to add tags.')
    parser.add_argument('-o', '--out', type=str, help='Output file.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-u', '--uniq', action='store_true', help='Remove duplicate log messages.')
    parser.add_argument('--config', type=str, help='Config directory.')

    args = parser.parse_args()

    # read config files
    cfg = read_dotfile(args.config, DOT_CONFIG)
    tag = read_dotfile(args.config, DOT_TAG)
    filter = read_dotfile(args.config, DOT_FILTER)

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
