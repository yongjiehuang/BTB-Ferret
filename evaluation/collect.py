import argparse
import os
import glob
import subprocess

import pandas as pd

def parse_stats_file(file_path) -> dict[str, list[str]]:
    with open(file_path, 'r') as f:
        lines: list[str] = f.readlines()
    
    datapoints: dict[str, list[str]] = {}
    
    blocks: list[list[str]] = []
    block: list[str] = []
    in_block = False
    for line in lines:
        if '---------- Begin Simulation Statistics' in line:
            block = []
            in_block = True
        elif '---------- End Simulation Statistics' in line:
            in_block = False
            blocks.append(block)
        elif in_block:
            block.append(line)
    
    for block in blocks:
        for line in block:
            chunks = line.split()
            if len(chunks) < 2:
                continue                
            key = chunks[0]
            if key.__contains__('\0'):
                continue
            if key not in datapoints:
                datapoints[key] = []
            value = chunks[1]
            datapoints[key].append(value)
    return datapoints
            


def main():
    our_arch = str.replace(subprocess.check_output(['dpkg', '--print-architecture']).decode("utf-8"), '\n', '') 
    
    parser = argparse.ArgumentParser(prog='Collector')
    parser.add_argument('--arch', type=str, default=our_arch, help='Architecture name')
    parser.add_argument('experiments', nargs="+", help='Name of experiments')

    args = parser.parse_args()

    result: pd.DataFrame = pd.DataFrame()

    for experiment in args.experiments:
        benchmarks = glob.glob(f'../results/{args.arch}/{experiment}/*/stats.txt')

        for benchmark in benchmarks:
            # The benchmark name is assumed to be the immediate subdirectory name.
            benchmark_name = os.path.basename(os.path.dirname(benchmark))
            data = parse_stats_file(benchmark)

            if not data:
                print(f"No data found in {benchmark}")
                continue
            
            experiment_name = f"{args.arch}_{experiment}"

            df = pd.DataFrame({k:pd.Series(v) for k,v in data.items()})

            print(f"\nData for Experiment {experiment_name} Benchmark {benchmark_name}:\n {df}\n")
            df = df.assign(experiment=experiment_name, benchmark=benchmark_name)
            result = pd.concat([result, df], ignore_index=True)
    
    # Save the result to a CSV file
    result.to_csv(f'results.csv', index=False)



if __name__ == '__main__':
    main()