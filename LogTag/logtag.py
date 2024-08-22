import argparse
import glob
import hjson
import os
import re
import sys
from tabulate import tabulate

# Define the directory for configuration files
DOTDIR = '.logtag'

# Define different paths for the current directory, working directory, and home directory
PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


# Class to represent a tag with a key, value, and category
class Tag:
    def __init__(self, key: str, value: str, category: str):
        self.key = key
        self.value = value
        self.category = category


# Class to represent a line from a log file
class Line:
    def __init__(self, file: str, line: str):
        self.file = file
        self.line = line


# Base class to read and load .logtag files based on patterns
class ReadDotFile:
    def __init__(self, argdirectory: str, filepattern: str, category: str):
        self.argdirectory = argdirectory
        self.filepattern = filepattern
        self.category = category

    # Method to extract category from the filename if a pattern is provided
    def get_category(self, filename: str) -> str:
        if self.category:
            match = re.match(self.category, filename)
            if match:
                return match.group(1)
        return None

    # Merge multiple configurations into a single dictionary
    def merge_configs(self, configs: dict) -> dict:
        final_config = {}
        for config in configs:
            final_config.update(config)
        return final_config

    # Load a configuration from a single file
    def load_config(self, filepath: str) -> dict:
        if os.path.exists(filepath):
            try:
                filename = os.path.basename(filepath)
                category = self.get_category(filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    lines = hjson.load(file)
                    if category:
                        config = {category: lines}
                    else:
                        config = lines
                    return config
            except hjson.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {filepath}.")
                return {}
        return {}

    # Load all configurations that match the file pattern in the directory
    def load_configs(self, directory: str) -> dict:
        configs = []
        if not os.path.exists(directory) or not os.listdir(directory):
            return {}
        regex = re.compile(self.filepattern)
        files = reversed(os.listdir(directory))
        for filename in files:
            if regex.match(filename):
                filepath = os.path.join(directory, filename)
                configs.append(self.load_config(filepath))
        return self.merge_configs(configs)

    # Load configurations with priority from multiple directories
    def load(self) -> dict:
        # Priority: arg_directory > CWD > HOME > PWD
        configs = []
        if self.argdirectory:
            configs.append(self.load_configs(self.argdirectory))
        configs.append(self.load_configs(os.path.join(CWD, DOTDIR)))
        configs.append(self.load_configs(os.path.join(HOME, DOTDIR)))
        configs.append(self.load_configs(os.path.join(PWD, DOTDIR)))
        return self.merge_configs(configs)


# Class to read configuration files named 'config.json'
class ReadDotFileConfig(ReadDotFile):
    def __init__(self, argdirectory: str):
        filepattern = r'^config\.(json|hjson)$'
        super().__init__(argdirectory, filepattern, None)

    # Override load method to handle 'config.json' files specifically
    def load(self) -> dict:
        return super().load()


# Class to read tag files matching certain patterns and extract categories
class ReadDotFileTag(ReadDotFile):
    def __init__(self, argdirectory: str):
        filepattern = r'^([0-9]+-.*-tag|[0-9]+-tag|tag)\.(json|hjson)$'
        category = r'^[0-9]+-(.*)-tag\.(json|hjson)$'
        super().__init__(argdirectory, filepattern, category)

    # Override load method to handle tag files specifically
    def load(self) -> dict:
        return super().load()


# Function to join lines from all files that match given files
def all_file_join(file_list: list) -> list:
    all_line = []
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = [Line(file, line.rstrip()) for line in lines]
            all_line += lines
    return all_line


# Main function to parse arguments and process log files
def main():
    parser = argparse.ArgumentParser(description='LogTag adds tags to log messages.')
    parser.add_argument('files', nargs='*', type=str, help='Files to add tags.')
    parser.add_argument('-f', '--file', type=str, nargs='+', help='Files to add tags.')
    parser.add_argument('-o', '--out', type=str, help='Output file.')
    parser.add_argument('-s', '--sort', action='store_true', help='Sort log messages.')
    parser.add_argument('-u', '--uniq', action='store_true', help='Remove duplicate log messages.')
    parser.add_argument('--hidden', action='store_true', help='Display hidden.')
    parser.add_argument('--config', type=str, help='Config directory.')

    args = parser.parse_args()

    # If --file/-f is used, override positional arguments
    if args.file:
        files = args.file
    else:
        files = args.files

    # If no files are provided, print an error message and exit
    if not files:
        print('Error: No input files. Use -f or provide file arguments.')
        sys.exit(1)

    # Join all log messages from the provided files
    all_files = []
    for pattern in files:
        file_list = glob.glob(pattern)
        for file in file_list:
            all_files.append(file)
    all_file = all_file_join(all_files)

    # Sort log messages if the sort option is specified
    if args.sort:
        all_file = sorted(all_file, key=lambda line: line.line)

    # Load configuration, tags from .logtag files
    cfg = ReadDotFileConfig(args.config).load()
    tag = ReadDotFileTag(args.config).load()

    # Extract the column configuration display settings
    column = cfg.get('column', [])

    # Initialize a list to hold the processed log messages
    log_messages = []

    # Helper function to format and store log messages based on the config
    def print_tp(msgs: list, line: Line) -> None:
        line_message = {}
        for col in column:
            if not col['enable']:
                continue
            title = col['display']
            match col['name']:
                case 'TAG':
                    line_message[title] = ', '.join([msg.value for msg in msgs])
                case 'CATEGORY':
                    line_message[title] = ', '.join([msg.category for msg in msgs])
                case 'FILE':
                    line_message[title] = line.file
                case 'LOG':
                    line_message[title] = line.line
        log_messages.append(line_message)

    # Process each line in the log files to apply tags
    for line in all_file:
        msg = []
        for ktag, vtag in tag.items():
            for key, value in vtag.items():
                if key in line.line:
                    msg.append(Tag(key, value, ktag))

        # If the unique option is specified, only process lines with tags
        if args.uniq:
            if len(msg) > 0:
                print_tp(msg, line)
            continue

        else:
            print_tp(msg, line)

    # Convert the processed log messages into a table format
    table = tabulate(log_messages, headers='keys', tablefmt='plain')

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
