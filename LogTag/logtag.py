import argparse
import glob
import os
import re
import sys
import hjson
from tabulate import tabulate


# Define the directory for configuration files
DOTDIR = '.logtag'

# Define different paths for the current directory, working directory, and home directory
PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


class Line:
    def __init__(self, file_path: str, log_line: str):
        self.file_path = file_path
        self.log_line = log_line


class Log:
    def __init__(self):
        self.lines: list[Line] = []

    def append(self, file_path: str, line: list) -> None:
        self.lines += [Line(file_path, l.rstrip()) for l in line]

    def soft(self) -> None:
        self.lines = sorted(self.lines, key=lambda line: line.log_line)


class MatchedTag:
    def __init__(self, category: str, word: str, msg: str):
        self.category = category
        self.word = word
        self.msg = msg


def read_log_files(file_list: list) -> Log:
    log = Log()
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            line = f.readlines()
            log.append(file, line)
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
    '''
    Main function to process log messages and add tags
    '''
    parser = argparse.ArgumentParser(description='LogTag adds tags to log messages.')
    parser.add_argument('files', type=str, nargs='*', help='Files to add tags.')
    parser.add_argument('-f', '--file', type=str, nargs='+', help='Files to add tags.')
    parser.add_argument('-c', '--category', type=str, nargs="*", help='Enable tag category.')
    parser.add_argument('-o', '--out', type=str, help='Output file.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-u', '--uniq', action='store_true', help='Remove duplicate log messages.')
    parser.add_argument('--hidden', action='store_true', help='Display hidden.')
    parser.add_argument('--config', type=str, help='Config directory.')
    args = parser.parse_args()

    # If --file/-f is used, override positional arguments
    if args.file:
        file_pattern_list = args.file
    else:
        file_pattern_list = args.files

    # If no files are provided, print an error message and exit
    if not file_pattern_list:
        print('Error: No input files. Use -f or provide file arguments.')
        sys.exit(1)

    # Join all log messages from the provided files
    file_list = []
    for file_pattern in file_pattern_list:
        glob_file_list = glob.glob(file_pattern)
        for glob_file in glob_file_list:
            file_list.append(glob_file)

    # Read log files and store log messages
    logs = read_log_files(file_list)

    # Sort log messages if the sort option is specified
    if args.sort:
        logs.soft()

    # Load configuration, tags from .logtag files
    config = load_config_file(args.config)

    # Extract the column configuration display settings
    column = config.get('column', [])

    # Extract the category configuration display settings
    category = config.get('category', [])

    # If the category option is specified, override the config
    if args.category:
        category = args.category

    # If no category is specified, set it to None
    if not category:
        category = None

    # Load logtag files and store the tags
    logtag = load_logtag_file(args.config)

    # Initialize a list to hold the processed log messages
    message = []

    # Helper function to format and store log messages based on the config
    def append_message(msgs: list[MatchedTag], line: Line) -> None:
        line_message = {}
        for col in column:
            if not col['enable']:
                continue
            title = col['display']
            match col['name']:
                case 'TAG':
                    line_message[title] = ', '.join([msg.msg for msg in msgs])
                case 'CATEGORY':
                    line_message[title] = ', '.join([msg.category for msg in msgs])
                case 'FILE':
                    line_message[title] = line.file_path
                case 'LOG':
                    line_message[title] = line.log_line
        message.append(line_message)

    # Process each line in the log files to apply tags
    for line in logs.lines:
        msg: list[MatchedTag] = []
        for tag_category, kv in logtag.items():
            # Skip if the category is specified and the tag category is not in the category list
            if category and tag_category not in category:
                continue

            # Check if the word in the tag category is in the log line
            for word, kmsg in kv.items():
                if word in line.log_line:
                    msg.append(MatchedTag(tag_category, word, kmsg))

        # If the unique option is specified, only process lines with tags
        if args.uniq:
            if len(msg) > 0:
                append_message(msg, line)
            continue

        else:
            append_message(msg, line)

    # Convert the processed log messages into a table format
    table = tabulate(message, headers='keys', tablefmt='plain')

    # Print the formatted log messages
    if not args.hidden:
        print(table)

    # Write the formatted log messages to an output file if specified
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(table)
            f.write('\n')


# Entry point of the script
if __name__ == '__main__':
    main()
