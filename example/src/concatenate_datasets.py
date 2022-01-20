import argparse

import pandas as pd

if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Concatenate two datasets.')
    parser.add_argument('--datasets', nargs='+', type=str, required=True, help='Paths to datasets')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    args = parser.parse_args()

    datasets = [pd.read_csv(path) for path in args.datasets]
    pd.concat(datasets).to_csv(args.output, index=False)
