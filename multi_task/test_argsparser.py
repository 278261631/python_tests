import argparse
import os
from datetime import datetime

default_subdir = datetime.now().strftime('%y%m%d')

parser = argparse.ArgumentParser(description='root_dir sub_dir')

parser.add_argument('root_dir', type=str, help='root dir like /home/mars/kats_test_data/data/')

parser.add_argument('--sub_dir', type=str, default=default_subdir, help='sub dir like 20250335')

args = parser.parse_args()
full_path = os.path.join(args.root_dir, args.sub_dir)
print(f" {full_path}")