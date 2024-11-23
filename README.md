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

This package is not yet registered on PyPI.

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

- `-o`, `--out`: Outputs the result to the specified file.
- `-s`, `--sort`: Sorts the log messages.
- `-u`, `--uniq`: !!!DEPRECATED!!! Displays only tagged messages.
- `-f`, `--filter`: Displays only tagged messages.
- `--hidden`: Does not output log messages to the console.
- `--config`: Specifies a custom configuration directory.
- `--config-first-directory-tag`: Loads custom tag file settings only from the first found directory.
- `--category`: Specifies one or more tag categories to filter log messages. If not specified, all categories are used.
- `--stop-first-tag`: Stops tagging a line as soon as the first tag is matched.
- `--stop-first-category`: Stops tagging a line as soon as the first category is matched.

## Configuration Files Overview

The configuration files for this system are structured in YAML format and consist of two main parts: the general settings (`config.yaml`) and category-specific log tag files (`lotgag/<number>-<category>.yaml`).

### `config.yaml`

```yaml
# Settings for the columns to be displayed in the log output.
column:
  - name: TAG
    display: TAG
    enable: true
  - name: CATEGORY
    display: CATEGORY
    enable: true
  - name: FILE
    display: LOG-FILE
    enable: true
  - name: LOG
    display: LOG
    enable: true

# Enable tag categories for filtering logs.
# Specify categories in the format "<tag>-<subtag>".
category:
  # - "default"
  # - "android"
  # - "android-kernel"
  # - "etc..."
```

- **`column`**: Defines the columns to be shown in the log output, including whether they are enabled and the display name for each column.
  - `name`: The internal name of the column.
  - `display`: The display name that will be shown in the log output.
  - `enable`: Whether the column should be shown (`true` to show, `false` to hide).
- **`category`**: Defines log tag categories for filtering purposes. You can add or remove categories depending on your needs. If all categories are valid, leave this section empty.

### Tag File (`lotgag/<number>-<category>.yaml`)

Each category can have its own log tag configuration file, structured as follows:

```yaml
- keyword: hoge-log
  message: hoge-message
- keyword: fuga.*log
  message: fuga-message
  regex: true
```

- **`<category>`**: The file name corresponds to the category name, and each file can define multiple keywords for that specific category.
- **`keyword`**: The specific log keyword to be matched.
- **`message`**: A description or explanation for the keyword.
- **`regex`**: Specifies if the keyword should be interpreted as a regular expression (`true`). If omitted, the keyword will be treated as a literal string.

### Directory Structure

The tool looks for configuration files in the following priority order:

1. The directory specified by the `--config` option
2. The current working directory
3. The user's home directory
4. The directory where the script is located

## Example

Below is an example of adding tags to log files, sorting the log messages, removing duplicates, and outputting the result to `output.txt`. Wildcards (`*.txt`) can be used to match multiple files:

```sh
$ logtag *.txt -o output.txt --sort --filter --config ./config
```

```sh
$ python logtag.py *.txt -o output.txt --sort --filter --config ./config
```

This command reads all `.txt` files in the current directory, adds tags, sorts and removes duplicates, and then outputs the result to `output.txt`. If a custom configuration directory is provided (via `--config`), the tool will look for `config.yaml` and `logtag.yaml` in that directory.
