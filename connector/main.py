import os
import sys

script_dir = os.path.dirname(__file__)
path_range = "../" * 3
mymodule_dir = os.path.join(script_dir, path_range)
sys.path.append(mymodule_dir)
from source_sftp import SourceSftp

from datapipes_images_utils.args_parser.utils import parse_args

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    source = SourceSftp(args)
    if args.command == "read":
        source.read()
