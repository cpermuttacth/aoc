#!/usr/bin/env python

def get_desc():
    return 3, 'Day 3: Toboggan Trajectory'


def calc(log, values, mode):
    from grid import Grid
    grid = Grid.from_text(values)
    ret = []

    if mode == 1:
        passes = [[3,1]]
    else:
        passes = [[1,1],[3,1],[5,1],[7,1],[1,2]]
    for step_x, step_y in passes:
        ret.append(0)
        x, y = 0, 0 
        while True:
            x += step_x
            y += step_y
            x = x % grid.width()
            if y >= grid.height():
                break
            if grid.get(x, y) == "#":
                ret[-1] += 1

    value = 1
    for x in ret:
        value *= x

    return value


def test(log):
    values = log.decode_values("""
        ..##.......
        #...#...#..
        .#....#..#.
        ..#.#...#.#
        .#...##..#.
        ..#.##.....
        .#.#.#....#
        .#........#
        #.##...#...
        #...##....#
        .#..#...#.#
    """)

    ret, expected = calc(log, values, 1), 7
    log("Test returned %s, expected %s" % (str(ret), str(expected)))
    if ret != expected:
        return False

    ret, expected = calc(log, values, 2), 336
    log("Test returned %s, expected %s" % (str(ret), str(expected)))
    if ret != expected:
        return False

    return True


def run(log, values):
    log(calc(log, values, 1))
    log(calc(log, values, 2))