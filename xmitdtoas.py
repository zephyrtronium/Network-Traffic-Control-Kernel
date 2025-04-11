#!/usr/bin/env python3

"""
Augment raw packet timestamps into rich timing metrics.

Input is expected to come in lines formatted as
    action=msg time=1234567890 key=12345
where action identifies the tracepoint, time is the timestamp in ns,
and key is an identifier for the packet. We assume that every packet
is traced in the same order and that packet keys are unique for the
lifetime of each packet.

Output is formatted as a CSV document with one row per packet, with the
first column representing the timestamp of the first action and each
successive column holding the time delta since the previous action.
"""


import sys
from typing import Iterator, Optional, Tuple, List


def parse(lines: Iterator[str]) -> Iterator[Tuple[str, int, int]]:
    """Parse lines into action name, timestamp, and key ID.

    Args:
        lines: Iterator of strings in the format
        "action=msg time=1234567890 key=12345"

    Yields:
        Tuples containing (action, timestamp, key) for lines that match
        the expected format.
    """
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 3:
            continue
        attrs = {}
        for kv in parts:
            p = kv.split('=')
            if len(p) != 2 or p[0] not in ['action', 'time', 'key']:
                break
            attrs[p[0]] = p[1]
        if len(attrs) != 3:
            continue
        try:
            yield attrs['action'], int(attrs['time']), int(attrs['key'])
        except ValueError:
            pass

def packets(actions: List[str], lines: Iterator[Tuple[str, int, int]]) -> Iterator[List[int]]:
    """Convert parsed trace lines into timing metrics.

    Args:
        actions: The actions to select. The first action in the list is
            considered the start of a packet. Packets for which the first
            observed action is not the first element of the list will be
            skipped.
        lines: An iterator of (action, time, key) tuples as produced by
            parse().

    Returns:
        An iterator of lists of timestamps associated with each packet.
        They may not be emitted in sorted time order.
    """
    times = {}
    for action, time, key in lines:
        try:
            k = actions.index(action)
        except ValueError:
            # No action. Skip this line.
            continue
        # Save this time for the packet.
        if key not in times:
            # If this isn't the first action that we expect,
            # it might be a resend for a packet we've already emitted.
            # Skip it in that case.
            if k != 0:
                continue
            times[key] = [None] * len(actions)
        # If we've already seen this action for it, keep the old time.
        if times[key][k] is None:
            times[key][k] = time
        # If we've seen all the actions for this packet, yield it.
        if all(x is not None for x in times[key]):
            yield times[key]
            del times[key]
    # Now input is exhausted. Everything that's left is an incomplete
    # packet. Discard it.
    if times:
        print(f"Warning: {len(times)} packets were not complete", file=sys.stderr)


def dtoas(times: List[int]) -> List[int]:
    """Convert a list of times to a list of times since the first.

    Args:
        times: A list of timestamps.

    Returns:
        A list of time deltas relative to the first timestamp.
    """
    return [times[0]] + [times[i] - times[0] for i in range(1, len(times))]


if __name__ == '__main__':
    for p in packets(['sendto', 'dev_start_xmit', 'dev_xmit'], parse(sys.stdin)):
        print(','.join(str(x) for x in dtoas(p)))
