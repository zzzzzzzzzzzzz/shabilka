# coding=utf-8
import argparse

from shabilka.basic import Alpha

if __name__ == '__main__':
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--file', '-f', type=str, help='path to the file with alphas', required=True)
    args = p.parse_args()
    filepath = args.file
    Alpha.load_to_db_from_file(filepath=filepath, debug=True)