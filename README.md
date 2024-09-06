# LogTag

LogTag is a tool for adding tags to log messages. This script reads log messages from specified files, adds tags, and optionally sorts and removes duplicates.

## Features

- Combine multiple log files
- Add tags to log messages
- Sort log messages
- Remove duplicate log messages
- Flexible customization through configuration files
- Supports regular expressions for tag matching

## Installation

### Install from PyPI

**TODO:** This package is not yet registered on PyPI.

```sh
pip install logtag
```

### Local Installation

To install this script locally, use the following command:

```sh
pip install -e .
```

## Usage

Run the script as follows:

```sh
logtag [files] -o [output_file] [options]
```

### Arguments

- `files`: Specify one or more log files to process. Wildcards are supported (e.g., `*.txt` to match all `.txt` files).

### Options

- `-c`, `--category`: Specify one or more tag categories to filter log messages by. If not provided, all categories will be used.
- `-o`, `--out`: Specify the output file. If not specified, the result will be printed to the standard output.
- `-s`, `--sort`: Sort the log messages by their content.
- `-u`, `--uniq`: Remove duplicate log messages. Only unique messages will be kept.
- `--hidden`: Display hidden log messages. By default, hidden log messages are not shown.
- `--config`: Specify a custom configuration directory containing `config.hjson` and tag files.

## Configuration Files

Configuration files are in HJSON format (which allows comments and more flexible syntax than JSON) and are structured as follows:

### `config.hjson`

```json
{
  "column": [
    { "name": "TAG", "display": "Tag", "enable": true },
    { "name": "CATEGORY", "display": "Category", "enable": true },
    { "name": "FILE", "display": "File", "enable": true },
    { "name": "LOG", "display": "Log Message", "enable": true }
  ]
}
```

- `column`: Specify the columns to display in the output, and their settings (e.g., visibility and display name).

### Tag File (`logtag.hjson`)

```json
{
  "ERROR": "Error detected",
  "INFO": "Informational message",
  "^WARN.*": "Warning message"
}
```

- Tags define specific keywords and their associated messages. When these keywords appear in the log, the corresponding message is added as a tag.
- **Regular expressions** are supported for tag matching. For example, the tag `^WARN.*` will match any log message starting with "WARN".

### Directory Structure

The tool looks for configuration files in the following priority order:

1. The directory specified by the `--config` option
2. The current working directory
3. The user's home directory
4. The directory where the script is located

## Example

Below is an example of adding tags to log files, sorting the log messages, removing duplicates, and outputting the result to `output.txt`. Wildcards (`*.txt`) can be used to match multiple files:

```sh
python logtag.py *.txt -o output.txt --sort --uniq --config ./config
```

This command reads all `.txt` files in the current directory, adds tags, sorts and removes duplicates, and then outputs the result to `output.txt`. If a custom configuration directory is provided (via `--config`), the tool will look for `config.hjson` and `logtag.hjson` in that directory.
