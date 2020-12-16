<img align="right" width="326" height="367" src="https://raw.githubusercontent.com/seligman/aoc/master/other/aoc_tree_small.png">

These are my solutions to the [Advent of Code](https://adventofcode.com/) puzzles.

The solutions are written in Python 3, though up to 2018, the code should also run in Python 2, for 2019 and on, it's probably not backwards compatible.  For the most part, code is designed to be quick to write rather than maintainable or easy to read.  I'm not quite playing code golf with this code, but I'm also not avoiding copy-n-paste and short variable names if it speeds up writing code.  I don't often make it to the leaderboards, but when I do, I'll show up as `seligman99` there.

In each year you can run `./advent.py run 1` to run a day's helper and see its output:

```
$ ./advent.py run 1
## Day 1: Not Quite Lisp
Entered basement on 1795
74
# That took 0.0005 seconds to complete
# Got expected output!
```

Each day also has a test harness to test the sample input for the day:

```
$ ./advent.py test 1
## Day 1: Not Quite Lisp
Entered basement on 1
That worked!
Done, 1 worked, 0 failed
```

`advent.py` has a bunch of other options, including the ability to run with other test input, run other commands in the helpers that support them, mostly for drawing animations, and prepare a new day.  Run it without any arguments to see what it can do.

Starting in 2019 I've started adding some animations to the respective yearly folders under `animations`.  These are simple attempts to visualize some of the puzzles as it's processed.

Two extra classes are common to the helpers, though they get expanded and modified from time to time:

* `Grid`: implemented in `grid.py` is a n-dimensional simple matrix class that supports arbitrary unbounded access, including negative positions.  Under the covers it's a wrapper around a defaultdict, and almost always slower than other options.  It does make writing code a bit faster.

* `Program`: implemented in `program.py` is a compiler/runner for the "int code" type puzzles.  It supports some basic debugging, and the ability to save state for cases where it's helpful to roll back the state machine. 

Also, I have a [simple ticker here](https://seligman.github.io/aoc_ticker.html) that counts down to a few minutes before another puzzle is unlocked.