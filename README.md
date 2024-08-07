# LogTag

LogTag is a tool for adding tags to log messages. This script reads log messages from specified files, adds tags, and optionally sorts and removes duplicates.

## Features

- Combine multiple log files
- Add tags to log messages
- Sort log messages
- Remove duplicate log messages
- Flexible customization through configuration files

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
python logtag.py -f [log_file1] [log_file2] ... -o [output_file] [options]
```

### Options

- `-f`, `--file`: Specify log files to add tags. Multiple files can be specified.
- `-o`, `--out`: Specify the output file. If not specified, the result will be printed to the standard output.
- `-s`, `--sort`: Sort log messages.
- `-u`, `--uniq`: Remove duplicate log messages.
- `--config`: Specify the configuration file.

## Configuration Files

Configuration files are in JSON format and are structured as follows:

### `config.json`

```json
{
  "space": 20
}
```

- `space`: Specify the space between the log message and the tag.

### Tag File (`tag.json`)

```json
{
  "ERROR": "Error",
  "INFO": "Info"
}
```

- Specify the tags corresponding to specific keywords in the log messages.

### Filter File (`filter.json`)

```json
{
  "display": ["ERROR", "WARN"]
}
```

- Specify the filter for displaying log messages.

## Priority

The search path for configuration files is determined by the following priority:

1. Directory specified in the command line
2. User's home directory
3. Current working directory
4. Directory where the script is located

## Example

Below is an example of adding tags to log files `log1.txt` and `log2.txt`, and outputting the result to `output.txt`:

```sh
python logtag.py -f log1.txt log2.txt -o output.txt --sort --uniq --config ./config
```

This command reads the specified log files, adds tags, sorts, and removes duplicates, and then outputs the result to `output.txt`.
