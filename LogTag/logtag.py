import argparse
import glob
import os
import re
import sys
import hjson
from tabulate import tabulate


DOTDIR = '.logtag'

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


class LogLine:
    def __init__(self, file_path: str, line: str):
        self.file_path = file_path
        self.line = line


class Log:
    def __init__(self):
        self.lines: list[LogLine] = []

    def append(self, file_path: str, lines: list[str]) -> None:
        self.lines += [LogLine(file_path, line.rstrip()) for line in lines]

    def soft(self) -> None:
        self.lines = sorted(self.lines, key=lambda line: line.line)


class MatchedTag:
    def __init__(self, category: str, keyword: str, message: str):
        self.category = category
        self.keyword = keyword
        self.message = message


def read_log_files(arg_files: list[str]) -> Log:
    log = Log()

    def read_file(file: str) -> Log:
        with open(file, 'r', encoding='utf-8') as f:
            line = f.readlines()
            log.append(file, line)

    for arg_file in arg_files:
        files = glob.glob(arg_file)
        for file in files:
            read_file(file)

    return log


def merge(configs: dict) -> dict:
    if not configs:
        return {}

    merge_config = {}
    for config in configs:
        if not config:
            continue
        merge_config.update(config)
    return merge_config


def load_files(directory: str, file_pattern: str, load_file) -> dict:
    if not os.path.exists(directory) or not os.listdir(directory):
        return {}

    file_regex = re.compile(file_pattern)

    configs = []
    files = reversed(os.listdir(directory))
    for file in files:
        if file_regex.match(file):
            filepath = os.path.join(directory, file)
            configs.append(load_file(filepath))

    merge_config = merge(configs)
    return merge_config


def load_config_file(arg_dir: str) -> dict:
    def load_file(file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return hjson.load(file)
        except hjson.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {file_path}.")
            return {}

    configs = []

    def load(directory: str) -> dict:
        if directory:
            config = load_files(directory, r'^config\.(json|hjson)$', load_file)
            configs.append(config)

    load(arg_dir)
    load(os.path.join(CWD, DOTDIR))
    load(os.path.join(HOME, DOTDIR))
    load(os.path.join(PWD, DOTDIR))

    merge_config = merge(configs)
    return merge_config


def load_logtag_file(arg_dir: str) -> dict:
    def cut_out_category(file_path: str) -> str:
        match = re.match(r'^[0-9]+-(.*)\.(json|hjson)$', file_path)
        if match:
            return match.group(1)
        return None

    def load_file(file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {}

        try:
            filename = os.path.basename(file_path)
            category = cut_out_category(filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                logtag = hjson.load(file)
                config = {category: logtag}
                return config
        except hjson.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {file_path}.")
            return {}

    configs = []

    def load(directory: str):
        if directory:
            directory = os.path.join(directory, 'logtag')
            if not os.path.exists(directory):
                return
            config = load_files(directory, r'^[0-9]+-.*\.(json|hjson)$', load_file)
            configs.append(config)

    load(arg_dir)
    load(os.path.join(CWD, DOTDIR))
    load(os.path.join(HOME, DOTDIR))
    load(os.path.join(PWD, DOTDIR))

    merge_config = merge(configs)
    return merge_config


def main():
    parser = argparse.ArgumentParser(description='LogTag adds tags to log messages.')
    parser.add_argument('files', type=str, nargs='+', help='Files to add tags.')
    parser.add_argument('-c', '--category', type=str, nargs="*", help='Enable tag category.')
    parser.add_argument('-o', '--out', type=str, help='Output file.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-u', '--uniq', action='store_true', help='Remove duplicate log messages.')
    parser.add_argument('--hidden', action='store_true', help='Display hidden.')
    parser.add_argument('--config', type=str, help='Config directory.')
    args = parser.parse_args()

    if not args.files:
        print("Error: No files provided.")
        sys.exit(1)

    logs = read_log_files(args.files)

    if args.sort:
        logs.soft()

    logtag = load_logtag_file(args.config)

    config = load_config_file(args.config)
    config_column = config.get('column', [])
    config_category = config.get('category', [])

    if args.category:
        config_category = args.category

    if not config_category:
        config_category = None

    message = []

    def append_message(matched_tags: list[MatchedTag], line: LogLine) -> None:
        message_line = {}

        for column in config_column:
            if not column['enable']:
                continue

            title = column['display']

            match column['name']:
                case 'TAG':
                    message_line[title] = ', '.join([msg.message for msg in matched_tags])
                case 'CATEGORY':
                    message_line[title] = ', '.join([msg.category for msg in matched_tags])
                case 'FILE':
                    message_line[title] = line.file_path
                case 'LOG':
                    message_line[title] = line.line

        message.append(message_line)

    for line in logs.lines:
        msg: list[MatchedTag] = []
        for tag_category, kv in logtag.items():
            if config_category and tag_category not in config_category:
                continue

            for word, kmsg in kv.items():
                if word in line.line:
                    msg.append(MatchedTag(tag_category, word, kmsg))

        if args.uniq:
            if len(msg) > 0:
                append_message(msg, line)
            continue

        else:
            append_message(msg, line)

    table = tabulate(message, headers='keys', tablefmt='plain')

    if not args.hidden:
        print(table)

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(table)
            f.write('\n')


if __name__ == '__main__':
    main()
