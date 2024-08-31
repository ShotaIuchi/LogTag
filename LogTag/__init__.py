import os

# Define the directory for configuration files
DOTDIR = '.logtag'

# Define different paths for the current directory, working directory, and home directory
PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
