#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys

BENCHMARK_RUNS = 5


def mean_and_std_dev(values: list[float]) -> (float, float):
    n = len(values)
    if n < 1:
        raise Exception("Cannot process empty values")

    mean = math.fsum(values) / n
    std_dev = math.sqrt(math.fsum([math.pow(v - mean, 2.0) for v in values]) / n)

    return mean, std_dev


def analyze_results(values: list[float]):
    clean_mean, clean_std_dev = mean_and_std_dev(values)
    print("\nBenchmark results:")
    print(f"  Mean: {clean_mean:.3f} s, standard deviation {clean_std_dev:.3f} s")


def extract_benchmark_time(process: subprocess.CompletedProcess) -> float:
    elapsed_time_match = re.findall(r"Elapsed time: ([0-9.]+)s, Critical Path: [0-9.]+s", process.stderr)
    if not elapsed_time_match or len(elapsed_time_match) > 1:
        print(f"ERROR: Expected result for elapsed time '{elapsed_time_match}'")
        sys.exit(1)
    return float(elapsed_time_match[0])


def run_benchmark_step(workspace: str, clean_cmd: list[str], benchmark_cmd: list[str]) -> float:
    print("\n>>> Ensure no cached results or runfile trees exist")
    subprocess.run(clean_cmd, cwd=workspace, check=True, capture_output=True)

    print("\n>>> Run benchmark")
    process = subprocess.run(benchmark_cmd, cwd=workspace, check=True, capture_output=True, text=True)
    benchmark_time = extract_benchmark_time(process)
    print(f"Elapsed time: {benchmark_time}")

    return benchmark_time


def run_benchmark(workspace: str, extra_args: list[str], extra_startup_args: list[str]) -> None:
    base_cmd = ["bazel"] + extra_startup_args + ["test"] + extra_args

    print(">>> Ensure all external deps are cached locally and show Python version\n")
    setup_cmd = base_cmd + ["some_test_0"]
    subprocess.run(setup_cmd, cwd=workspace, check=True)

    benchmark_times = [run_benchmark_step(
        workspace=workspace,
        clean_cmd=["bazel"] + extra_startup_args + ["clean"],
        benchmark_cmd=base_cmd + ["//..."])
        for _ in range(0, BENCHMARK_RUNS)]

    analyze_results(benchmark_times)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'workspace',
        type=str,
        help="Which project to use for running the benchmark"
    )
    parser.add_argument(
        '--extra_args',
        type=str,
        nargs='+',
        help="Further arguments for the benchmarked Bazel commands. Provide arguments without leading '--'"
    )
    parser.add_argument(
        '--extra_startup_args',
        type=str,
        nargs='+',
        help="Further startup arguments for the benchmarked Bazel commands. Provide arguments without leading '--'"
    )
    args = parser.parse_args()

    bazel_extra_args = [f"--{bazel_arg}" for bazel_arg in args.extra_args] if args.extra_args else []
    bazel_extra_startup_args = [f"--{bazel_arg}" for bazel_arg in args.extra_args] if args.extra_args else []

    run_benchmark(workspace=args.workspace, extra_args=bazel_extra_args, extra_startup_args=bazel_extra_startup_args)
