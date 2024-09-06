import argparse
import glob
import os
import re
import sys
import hjson
from tabulate import tabulate
from typing import Callable


DOTDIR = '.logtag'

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


class LineEx:
    def __init__(self, file_path: str, line: str):
        self.file_path = file_path
        self.line = line


class TagEx:
    def __init__(self, keyword: str, message: str):
        self.keyword = keyword
        self.message = message
        self.pattern = re.compile(keyword)


class TagCategory:
    def __init__(self, category: str, tags: list[TagEx]):
        self.category = category
        self.tags = tags


class MatchedTag:
    def __init__(self, category: str, keyword: str, message: str):
        self.category = category
        self.keyword = keyword
        self.message = message


class LoadConfig:
    def __init__(self, args: argparse.Namespace):
        self.settings = self._load_settings(args)
        self.tags: list[TagCategory] = self._load_tags(args)
        self.columns = self._get_column(args)
        self.category = self._get_category(args)

    def _get_column(self, args: argparse.Namespace) -> list[str]:
        column = self.settings.get('column', [])
        return column

    def _get_category(self, args: argparse.Namespace) -> list[str]:
        category = self.settings.get('category', [])

        if args.category:
            category = args.category

        if not category:
            category = None

        return category

    def _load_settings(self, args: argparse.Namespace) -> dict:
        def _load_file(file_path: str) -> dict:
            if not os.path.exists(file_path):
                return {}
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return hjson.load(file)
            except hjson.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {file_path}.")
                return {}

        def _load_impl(directory: str) -> dict:
            if not directory:
                return {}

            config = self._load_directory(directory, r'^config\.(json|hjson)$', _load_file)
            return config

        return self._load_directories(args, _load_impl)

    def _load_tags(self, args: argparse.Namespace) -> list[TagCategory]:
        def _cut_out_category(file_path: str) -> str:
            match = re.match(r'^[0-9]+-(.*)\.(json|hjson)$', file_path)
            if match:
                return match.group(1)
            return None

        def _load_file(file_path: str) -> dict:
            if not os.path.exists(file_path):
                return {}

            try:
                filename = os.path.basename(file_path)
                category = _cut_out_category(filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    logtag = hjson.load(file)
                    config = {category: logtag}
                    return config
            except hjson.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {file_path}.")
                return {}

        def _load_impl(directory: str) -> dict:
            if not directory:
                return {}

            directory = os.path.join(directory, 'logtag')
            if not os.path.exists(directory):
                return {}

            config = self._load_directory(directory, r'^[0-9]+-.*\.(json|hjson)$', _load_file)
            return config

        def _convert_to_tagcategory(config: dict) -> list[TagCategory]:
            tagcategories = []
            for category, tags in config.items():
                tagexs = []
                for keyword, message in tags.items():
                    tagexs.append(TagEx(keyword, message))
                tagcategories.append(TagCategory(category, tagexs))
            return tagcategories

        configs = self._load_directories(args, _load_impl)
        return _convert_to_tagcategory(configs)

    def _load_directories(self, args: argparse.Namespace, load: Callable[[str], dict]) -> dict:
        configs = []
        configs.append(load(args.config))
        configs.append(load(os.path.join(CWD, DOTDIR)))
        configs.append(load(os.path.join(HOME, DOTDIR)))
        configs.append(load(os.path.join(PWD, DOTDIR)))

        merge_config = self._merge(configs)
        return merge_config

    def _load_directory(self, directory: str, file_pattern: str, load_file: Callable[[str], dict]) -> dict:
        if not os.path.exists(directory) or not os.listdir(directory):
            return {}

        file_regex = re.compile(file_pattern)

        configs = []
        files = reversed(os.listdir(directory))
        for file in files:
            if file_regex.match(file):
                filepath = os.path.join(directory, file)
                configs.append(load_file(filepath))

        merge_config = self._merge(configs)
        return merge_config

    def _merge(self, configs: dict) -> dict:
        if not configs:
            return {}

        merge_config = {}
        for config in configs:
            if not config:
                continue
            merge_config.update(config)

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
    args: argparse.Namespace = parser.parse_args()

    if not args.files:
        print("Error: No files provided.")
        sys.exit(1)

    def _load_log(args: argparse.Namespace) -> list[LineEx]:
        def _load_file(file: str) -> list[LineEx]:
            if not os.path.exists(file):
                return []

            with open(file, 'r', encoding='utf-8') as fp:
                line = fp.readlines()
                return [LineEx(file, line.rstrip()) for line in line]

        lines: list[LineEx] = []

        for arg_file in args.files:
            files = glob.glob(arg_file)

            if not files:
                print(f"Warning: No files matched pattern: {arg_file}")

            for file in files:
                lines += _load_file(file)

        if args.sort:
            lines = sorted(lines, key=lambda line: line.line)

        return lines

    def _message(columns: list[dict[str, str]], line: LineEx, matched_tags: list[MatchedTag]) -> dict[str, str]:
        message: dict[str, str] = {}
        for column in columns:
            if not column['enable']:
                continue
            title = column['display']
            match column['name']:
                case 'TAG':
                    message[title] = ', '.join([matched_tag.message for matched_tag in matched_tags])
                case 'CATEGORY':
                    message[title] = ', '.join([matched_tag.category for matched_tag in matched_tags])
                case 'FILE':
                    message[title] = line.file_path
                case 'LOG':
                    message[title] = line.line
        return message

    logs = _load_log(args)
    config = LoadConfig(args)

    message: list[dict[str, str]] = []
    for line in logs:
        matched_tags: list[MatchedTag] = []
        for tag_category in config.tags:
            if config.category and (tag_category.category not in config.category):
                continue
            for tag_tag in tag_category.tags:
                if tag_tag.pattern.search(line.line):
                    matched_tags.append(MatchedTag(tag_category.category, tag_tag.keyword, tag_tag.message))

        if not args.uniq or len(matched_tags) > 0:
            message.append(_message(config.columns, line, matched_tags))

    table = tabulate(message, headers='keys', tablefmt='plain')

    if not args.hidden:
        print(table)

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(table)
            f.write('\n')


if __name__ == '__main__':
    main()
