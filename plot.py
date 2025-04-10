#!/usr/bin/env python3

import sys
from typing import Iterator

import matplotlib.pyplot as plt


def load_xmit(file: Iterator[str]) -> list[list[int]]:
    """
    Loads a CSV file containing time deltas.

    Args:
        file: Lines in the CSV file.

    Returns:
        Data in the CSV.
    """
    return [list(map(int, row.split(','))) for row in file]

def plot_latency(starts: list[int], latencies: list[int], output: str = 'latency_plot.png') -> None:
    """
    Plots latency (y-axis) against packet ID (x-axis).

    Args:
        starts: Start times of packets.
        latencies: Latencies of packets.
    """
    packet_ids = range(len(latencies))
    plt.plot(packet_ids, latencies, marker="o", linestyle="-", color="b", label="Latency")
    plt.xlabel("Packet Time (ns)")
    plt.ylabel("Latency (ns)")
    plt.title("Latency vs Packet Time")
    plt.grid(True)
    plt.legend()
    plt.savefig(output, format="png", dpi=300)

if __name__ == '__main__':
    inp = 'comm_sendeth.csv'
    if len(sys.argv) > 1:
        inp = sys.argv[1]
    with open(inp, 'r') as f:
        rows = load_xmit(f)
    cols = [[row[i] for row in rows] for i in range(len(rows[0]))]
    plot_latency(cols[0], cols[-1], output='latency_plot.png')
