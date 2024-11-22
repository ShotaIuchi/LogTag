import argparse
import glob
import os
import re
import sys
import yaml
import LogTag
from tabulate import tabulate
from typing import Callable


DOTDIR = '.logtag'

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


class Config:
    def __init__(self, columns: dict[str], categorys: dict[str]):
        self.columns = columns
        self.categorys = categorys


class LogLine:
    def __init__(self, file: str, line: str):
        self.file = file
        self.line = line


class KeyMsg:
    def __init__(self, keyword: str, message: str, regex: bool = True):
        self.keyword = keyword
        self.message = message
        if regex:
            self.pattern = re.compile(keyword)
        else:
            self.pattern = None


class Category:
    def __init__(self, priority: int, category: str):
        self.priority = priority
        self.category = category


class CategoryKeyMsgs:
    def __init__(self,  category: Category, kms: list[KeyMsg]):
        self.category = category
        self.kms = kms


class CategoryKeyMsg:
    def __init__(self, category: Category, km: KeyMsg):
        self.category = category
        self.km = km


class LineCategoryKeyMsg:
    def __init__(self, line: LogLine, ckm: list[CategoryKeyMsg]):
        self.line = line
        self.ckm = ckm


def dot_dirs(ARGS: argparse.Namespace) -> list[str]:
    dirs = []
    dirs.append(ARGS.config)
    dirs.append(os.path.join(PWD, DOTDIR))
    dirs.append(os.path.join(HOME, DOTDIR))
    dirs.append(os.path.join(CWD, DOTDIR))
    return dirs


def load_config(ARGS: argparse.Namespace) -> Config:
    dirs = dot_dirs(ARGS=ARGS)
    for dir in dirs:
        if not dir:
            continue
        if not os.path.exists(dir):
            continue

        config_path = os.path.join(dir, 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as fp:
                # first found config file is used
                loaded_config = yaml.safe_load(fp)
                config = Config(loaded_config.get('column', []), loaded_config.get('category', []))
                return config
    return None


def load_ckms(ARGS: argparse.Namespace) -> list[CategoryKeyMsgs]:
    dirs = dot_dirs(ARGS=ARGS)
    kms = []
    match = re.compile(r'(^[0-9]+)-(.*)\.ya*ml$')

    for dir in dirs:
        if not dir:
            continue
        if not os.path.exists(dir):
            continue

        km_dir = os.path.join(dir, 'logtag')
        if not os.path.exists(km_dir):
            continue

        for km_path in os.listdir(km_dir):
            if not km_path.endswith('.yaml') and not km_path.endswith('.yml'):
                continue

            conifg_data = match.search(km_path)
            if not conifg_data:
                continue
            if conifg_data.end() < 2:
                continue

            with open(os.path.join(km_dir, km_path), 'r', encoding='utf-8') as fp:
                loaded_kms = yaml.safe_load(fp)
                if not loaded_kms:
                    continue

                category = Category(conifg_data.group(1), conifg_data.group(2))
                km = [KeyMsg(tag['keyword'], tag['message'], tag.get('regex', False)) for tag in loaded_kms]
                ckm = CategoryKeyMsgs(category, km)
                kms.append(ckm)

    kms.sort(key=lambda x: x.category.category)
    kms.sort(key=lambda x: x.category.priority)
    return kms


def load_log(ARGS: argparse.Namespace) -> list[LogLine]:
    logs = []
    for file in ARGS.files:
        files = glob.glob(file)
        if not files:
            print(f"Warning: No files matched pattern: {file}")

        for file in files:
            if not os.path.exists(file):
                continue

            with open(file, 'r', encoding='utf-8') as fp:
                line = fp.readlines()
                logs += [LogLine(file, line.rstrip()) for line in line]

    if ARGS.sort:
        logs = sorted(logs, key=lambda log: log.line)

    return logs


def main():
    parser = argparse.ArgumentParser(description='LogTag adds tags to log messages.')
    parser.add_argument('files', type=str, nargs='+', help='Files to add tags.')
    parser.add_argument('-c', '--category', type=str, nargs="*", help='Enable tag category.')
    parser.add_argument('-o', '--out', type=str, help='Output file.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-u', '--uniq', action='store_true', help='Remove duplicate log messages.')
    parser.add_argument('--hidden', action='store_true', help='Display hidden.')
    parser.add_argument('--config', type=str, help='Config directory.')
    parser.add_argument('--stop-first-tag', action='store_true', help='Stop tagging upon hitting the first tag.')
    parser.add_argument('--stop-first-category', action='store_true', help='Stop tagging upon hitting the first category.')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {LogTag.__version__}')

    ARGS: argparse.Namespace = parser.parse_args()

    if not ARGS.files:
        print("Error: No files provided.")
        sys.exit(1)

    CONFIG = load_config(ARGS)
    KEYMSG = load_ckms(ARGS)
    LOGLINES = load_log(ARGS)

    CATEGORY = ARGS.category or CONFIG.categorys or None

    # match
    lineAndCategoryKeyMsgs: list[LineCategoryKeyMsg] = []
    for line in LOGLINES:
        lckm = LineCategoryKeyMsg(line, [])
        for ckm in KEYMSG:
            if ((CATEGORY) and (ckm.category in CATEGORY)):
                continue
            for km in ckm.kms:
                if km.pattern is not None:
                    if km.pattern.search(line.line):
                        lckm.ckm.append(CategoryKeyMsg(ckm.category, km))
                        if ARGS.stop_first_tag:
                            break
                else:
                    if km.keyword in line.line:
                        lckm.ckm.append(CategoryKeyMsg(ckm.category, km))
                        if ARGS.stop_first_tag:
                            break

            if len(lckm.ckm) > 0:
                if ARGS.stop_first_category or ARGS.stop_first_tag:
                    break

        if not ARGS.uniq or len(lckm.ckm) > 0:
            lineAndCategoryKeyMsgs.append(lckm)

    # convert table format
    table_data: list[dict[str, str]] = []
    for lckm in lineAndCategoryKeyMsgs:
        data: dict[str, str] = {}
        for column in CONFIG.columns:
            if column['enable']:
                title = column['display']
                match column['name']:
                    case 'TAG':
                        data[title] = ', '.join([ckm.km.message for ckm in lckm.ckm])
                    case 'CATEGORY':
                        data[title] = ', '.join([ckm.category.category for ckm in lckm.ckm])
                    case 'FILE':
                        data[title] = lckm.line.file
                    case 'LOG':
                        data[title] = lckm.line.line
        table_data.append(data)

    # output
    table = tabulate(table_data, headers='keys', tablefmt='plain')

    if not ARGS.hidden:
        print(table)

    if ARGS.out:
        with open(ARGS.out, 'w', encoding='utf-8') as f:
            f.write(table)
            f.write('\n')


if __name__ == '__main__':
    main()
