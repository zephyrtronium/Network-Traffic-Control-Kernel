# Network Traffic Control Kernel

This project produces metrics regarding IP packet latencies as they traverse
the Linux network stack.

`ntck.bash` builds helper programs, collects metrics, and produces plots.

## Requirements

The script must be run as root in the same working directory as the other files.

- Linux >= 6.1 (we use the most recent Debian)
- Linux headers (`apt install linux-headers-$(uname -r)`)
- bpftrace
- python3
- gcc (`apt install build-essential`)

If not specifying `$INTERFACE` per below:

- ip (`apt install iproute2` if it isn't already installed)
- jq

## Options

The `INTERFACE` environment variable specifies the network interface to use for sending packets.
If it is empty, ntck.bash uses `ip` and `jq` to select the first active interface.
You can specify it yourself when running by using a command like `sudo INTERFACE=lo1 ./ntck.bash`.

The `NTCK_DIR` environment variable specifies the output directory for artifacts and intermediate data.
If it is empty, a temporary directory is created.
Useful for debugging.

## Authors

- [Branden Brown](https://github.com/zephyrtronium)
- [Joshua Hellauer](https://github.com/joshhellauer)
- [Kendal Kalanish](https://github.com/kck43)
