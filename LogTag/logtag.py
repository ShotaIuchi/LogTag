import argparse
import json
import os
import re
import sys
from tempfile import TemporaryFile
from wcwidth import wcswidth
from tabulate import tabulate
from enum import Enum

DOTDIR = '.logtag'

DOT_CONFIG = 'config.json'
DOT_TAG = r'^([0-9]+-.*-tag|[0-9]+-tag|tag)\.json$'
DOT_FILTER = r'^([0-9]+-.*-filter|[0-9]+-filter|filter)\.json$'

DOT_CATEGORY = r'^[0-9]+-(.*)-tag\.json$'

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


class ELog(Enum):
    LOG = 0
    FILE = 1


class EConfig(Enum):
    MSG = 0
    FILE = 1


# join all files
def all_file_join(file_list: list) -> list:
    all_line = []
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = [[line.rstrip(), file] for line in lines]
            all_line += lines

    return all_line


# load config file
def load_config(file_path: str) -> dict:
    if os.path.exists(file_path):
        category = ''
        filename = os.path.basename(file_path)
        match = re.match(DOT_CATEGORY, filename)
        if match:
            category = match.group(1)
        else:
            print("No match found.")

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = json.load(file)
            config = {}
            for k, v in lines.items():
                config[k] = [v, category]
            return config
    return {}


# merge config files
def merge_configs(configs: dict) -> dict:
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
        files = reversed(files)  # コミットを別にするの注意
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

    space = cfg['space'][EConfig.MSG.value]
    filter_display = filter['display'][EConfig.MSG.value]

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
    log_messages = []

    def print_tp(msg: list, line: str) -> None:
        category = ''
        message = ''
        for m in msg:
            message = m[EConfig.MSG.value]
            if (category != ''):
                category += ','
            category += m[EConfig.FILE.value]
        log_messages.append({'category': category, 'message': message, 'file': line[ELog.FILE.value], 'log': line[ELog.LOG.value]})

    # convert log messages
    for line in all_file:
        msg = []
        for key, value in tag.items():
            if key in line:
                msg.append(value)

        # remove duplicate log messages
        if args.uniq:
            print_tp(msg, line)
            continue

        if len(filter_display) > 0:
            # filter log messages
            for key in filter_display:
                if key in line:
                    print_tp(msg, line)
                    break
        else:
            print_tp(msg, line)

    # convert log messages to table
    table = tabulate(log_messages, headers='keys', tablefmt='plain')

    # print converted log messages
    print(table)

    # write converted log messages to output file
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(table)
            f.write('\n')


if __name__ == '__main__':
    main()
