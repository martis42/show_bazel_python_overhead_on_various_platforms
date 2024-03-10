#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from dataclasses import dataclass

BENCHMARK_RUNS = 5


@dataclass
class BenchmarkResult:
    clean_time: float
    retest_time: float


def extract_benchmark_time(process: subprocess.CompletedProcess) -> float:
    elapsed_time_match = re.findall(r"Elapsed time: ([0-9.]+)s, Critical Path: [0-9.]+s", process.stderr)
    if not elapsed_time_match or len(elapsed_time_match) > 1:
        print(f"ERROR: Expected result for elapsed time '{elapsed_time_match}'")
        sys.exit(1)
    return float(elapsed_time_match[0])


def run_benchmark(workspace: str, extra_args: list[str]) -> BenchmarkResult:
    print("\n>>> Ensure no cached results or runfile trees exist")
    subprocess.run(["bazel", "clean"], cwd=workspace, check=True, capture_output=True)

    print("\n>>> Run benchmark\n")
    clean_cmd = ["bazel", "test"] + extra_args + ["//..."]
    process = subprocess.run(clean_cmd, cwd=workspace, check=True, capture_output=True, text=True)
    clean_time = extract_benchmark_time(process)
    print(f"Clean time: {clean_time}")

    retest_cmd = ["bazel", "test", "--nocache_test_results"] + extra_args + ["//..."]
    process = subprocess.run(retest_cmd, cwd=workspace, check=True, capture_output=True, text=True)
    retest_time = extract_benchmark_time(process)
    print(f"Retest time: {retest_time}")

    return BenchmarkResult(clean_time=clean_time,retest_time=retest_time)


def mean_and_std_dev(values: list[float]) -> (float, float):
    n = len(values)
    if n < 1:
        raise Exception("Cannot process empty values")

    mean = math.fsum(values) / n
    std_dev = math.sqrt(math.fsum([math.pow(v - mean, 2.0) for v in values]) / n)

    return mean, std_dev


def analyze_results(values: list[BenchmarkResult]):
    clean_mean, clean_std_dev = mean_and_std_dev([result.clean_time for result in values])
    retest_mean, retest_std_dev = mean_and_std_dev([result.retest_time for result in values])

    print("\nBenchmark results for clean run:")
    print(f"  Mean: {clean_mean:.3f} s, standard deviation {clean_std_dev:.3f} s")
    print("Benchmark results for retest:")
    print(f"  Mean: {retest_mean:.3f} s, standard deviation {retest_std_dev:.3f} s")


def main(workspace: str, extra_args: list[str]):
    print(">>> Ensure all external deps are cached locally and show Python version\n")
    subprocess.run(["bazel", "test", "some_test_0"], cwd=workspace, check=True)

    benchmark_times = [run_benchmark(workspace=workspace, extra_args=extra_args) for _ in range(0, BENCHMARK_RUNS)]
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
    args = parser.parse_args()

    bazel_extra_args = [f"--{bazel_arg}" for bazel_arg in args.extra_args] if args.extra_args else []
    main(workspace=args.workspace, extra_args=bazel_extra_args)
