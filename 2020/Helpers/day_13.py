#!/usr/bin/env python3

def get_desc():
    return 13, 'Day 13: Shuttle Search'

def chinese_remainder(values):
    prod = 1
    for _, n in values:
        prod *= n
    total = 0
    for val, n in values:
        b = prod // n
        total += val * b * pow(b, n - 2, n)
        total %= prod
    return total

def calc(log, values, mode):
    if mode == 1:
        ts = int(values[0])
        bus = [int(x) for x in values[1].split(",") if x != "x"]

        best = None
        best_val = None

        for cur in bus:
            if ts % cur == 0:
                best = cur
                best_val = ts
            else:
                off = cur - (ts % cur)
                target = ts + off
                if best_val is None or target < best_val:
                    best_val = target
                    best = cur
        return (best_val - ts) * best
    else:
        bus = [int(x) if x != "x" else -1 for x in values[1].split(",")]
        off = [(bus[x]-x,bus[x]) for x in range(len(bus)) if bus[x] > 0]
        return chinese_remainder(off)

def test(log):
    values = log.decode_values("""
        939
        7,13,x,x,59,x,31,19
    """)

    log.test(calc(log, values, 1), 295)
    log.test(calc(log, values, 2), 1068781)

def run(log, values):
    log(calc(log, values, 1))
    log(calc(log, values, 2))
