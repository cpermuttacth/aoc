#!/usr/bin/env python3

from command_opts import opt, main_entry
import utils
import os
import subprocess
import re
import textwrap
import time
import sys
import codecs
from datetime import datetime
from advent_year import YEAR_NUMBER

ALT_DATA_FILE = None
SOURCE_CONTROL = "p4"
DESC = """
### The suggested dail routine looks like this:
advent.py launch      # This launches some useful links
advent.py make_day    # This makes a day, only run it when the site is ready
advent.py test cur    # This tests the current day, keep going till it works!
advent.py run cur     # This runs on the same data
### And finally, when everything's done, some clean up, and make a comment to post
advent.py run_save cur dl_day cur get_index gen_comment
"""

class Logger:
    def __init__(self):
        self.rows = []

    def __call__(self, value):
        self.show(value)

    def show(self, value):
        global _print_catcher
        if _print_catcher is not None:
            _print_catcher.safe = True
        try:
            if isinstance(value, unicode): # pylint: disable=undefined-variable
                value = value.replace(u"\r\n", u"\n")
                for cur in value.split(u"\n"):
                    cur += u"\n"
                    self.rows.append(cur.encode("utf-8"))
                    sys.stdout.write(cur)
                sys.stdout.flush()
            else:
                value = str(value)
                value = value.replace("\r\n", "\n")
                for cur in value.split("\n"):
                    cur += "\n"
                    self.rows.append(cur)
                    sys.stdout.write(cur)
                sys.stdout.flush()
        except:
            value = str(value)
            value = value.replace("\r\n", "\n")
            for cur in value.split("\n"):
                cur += "\n"
                self.rows.append(cur)
                sys.stdout.write(cur)
            sys.stdout.flush()
        if _print_catcher is not None:
            _print_catcher.safe = False

    def save_to_file(self, filename):
        with open(filename, "w") as f:
            for cur in self.rows:
                f.write(cur)

    def compare_to_file(self, filename):
        if len(self.rows) == 0:
            return False
        i = 0
        with open(filename) as f:
            for cur in f:
                if i >= len(self.rows):
                    return False
                if self.rows[i] != cur:
                    return False
                i += 1
        if i != len(self.rows):
            return False
        return True

    def decode_values(self, values):
        ret = values.replace("\t", "    ").split("\n")
        # Only remove empty lines at the start and end
        while len(ret) > 0 and len(ret[0].strip()) == 0:
            ret = ret[1:]
        while len(ret) > 0 and len(ret[-1].strip()) == 0:
            ret = ret[:-1]
        # Remove the indenting based off the first line
        if len(ret) > 0:
            pad = len(ret[0]) - len(ret[0].lstrip(' '))
            pad -= pad % 4
        if pad > 0 and len(ret) > 0:
            for i in range(len(ret)):
                if ret[i].startswith(" " * pad):
                    ret[i] = ret[i][pad:]
        return ret

    def test(self, actual, expected):
        self.show("Test returned %s, expected %s" % (str(actual), str(expected)))
        if actual != expected:
            raise ValueError("Test failure")


def edit_file(filename):
    if SOURCE_CONTROL is not None:
        if SOURCE_CONTROL == "p4":
            cmd = ["p4", "edit", filename]
            print("$ " + " ".join(cmd))
            subprocess.check_call(cmd)
        elif SOURCE_CONTROL == "git":
            pass
        else:
            raise Exception()


def add_file(filename):
    if SOURCE_CONTROL is not None:
        if SOURCE_CONTROL == "p4":
            cmd = ["p4", "add", filename]
            print("$ " + " ".join(cmd))
            subprocess.check_call(cmd)
        elif SOURCE_CONTROL == "git":
            pass
        else:
            raise Exception()


def revert_file(filename):
    if SOURCE_CONTROL is not None:
        if SOURCE_CONTROL == "p4":
            cmd = ["p4", "revert", filename]
            print("$ " + " ".join(cmd))
            subprocess.check_call(cmd)
        elif SOURCE_CONTROL == "git":
            pass
        else:
            raise Exception()

@opt("Update all advent.py files")
def update_selfs():
    with open("advent.py", "rb") as f:
        source_data = f.read()

    for year in os.listdir(".."):
        if re.search("^[0-9]{4}$", year) is not None:
            year = os.path.join("..", year)
            if os.path.isdir(year):
                dest = os.path.join(year, "advent.py")
                with open(dest, "rb") as f:
                    dest_data = f.read()
                if dest_data == source_data:
                    print("%s is already up to date" % (dest,))
                else:
                    print("Updating %s..." % (dest,))
                    edit_file(dest)
                    with open(dest, "wb") as f:
                        f.write(source_data)


@opt("Use alt data file")
def alt(file_number):
    global ALT_DATA_FILE
    ALT_DATA_FILE = int(file_number)


def get_input_file(helper, file_type="input"):
    global ALT_DATA_FILE
    if ALT_DATA_FILE is None or ALT_DATA_FILE == 0:
        fn = "day_%02d_%s.txt" % (helper.get_desc()[0], file_type)
    else:
        fn = "day_%02d_%s_alt_%02d.txt" % (helper.get_desc()[0], file_type, ALT_DATA_FILE)
    return os.path.join("Puzzles", fn)


@opt("Generate a comment based off scores")
def gen_comment():
    max_day = 0
    for helper in utils.get_helpers():
        max_day = max(helper.get_desc()[0], max_day)
    
    scores_url = "https://adventofcode.com/2020/leaderboard/self"
    score_re = re.compile(r"^ *(?P<day>\d+) +\d+:\d+:\d+ +(?P<score1>\d+) +\d+ +\d+:\d+:\d+ +(?P<score2>\d+) +\d+ *$")
    scores = get_page(scores_url)

    found = False
    day, score1, score2 = -1, -1, -1

    for cur in scores.split("\n"):
        m = score_re.search(cur)
        if m is not None:
            day, score1, score2 = int(m.group("day")), int(m.group("score1")), int(m.group("score2"))
            if day == max_day:
                found = True
                break
    
    print("-" * 70)

    if not found:
        print("Warning: Couldn't find day!")
        print("")
    
    print("Python, %d / %d" % (score1, score2))
    print("")
    print("[github](https://github.com/seligman/aoc/blob/master/2020/Helpers/day_%02d.py)" % (max_day,))


@opt("Launch website")
def launch():
    urls = [
        "https://imgur.com/upload",
        "https://www.reddit.com/r/adventofcode/",
        "https://adventofcode.com/" + YEAR_NUMBER,
    ]

    for url in urls:
        if os.name == 'nt':
            cmd = "cmd /c start %s" % (url,)
        else:
            cmd = "open %s" % (url,)
        subprocess.check_call(cmd.split(' '))


@opt("Show other commands for a day")
def show_others(helper_day):
    sys.path.insert(0, 'Helpers')
    for helper in get_helpers_id(helper_day):
        print("## %s" % (helper.get_desc()[1]))
        found = False
        for cur in dir(helper):
            if cur.startswith("other_"):
                print("%s - %s" % (cur[6:], getattr(helper, cur)(True, None)))
                found = True
        if not found:
            print("(No other commands found)")


@opt("Run other command for a day")
def run_other(helper_day, command):
    sys.path.insert(0, 'Helpers')
    for helper in get_helpers_id(helper_day):
        found = False
        for cur in dir(helper):
            if cur == "other_" + command.lower():
                with open(get_input_file(helper)) as f:
                    values = []
                    for sub in f:
                        values.append(sub.strip("\r\n"))
                getattr(helper, cur)(False, values)
                found = True
        if not found:
            print("## %s" % (helper.get_desc()[1]))
            print("ERROR: Unable to find '%s'" % (command,))


@opt("Make new day (Offline)")
def make_day_offline(target_day="cur"):
    make_day_helper(True, force_day=target_day)


@opt("Make new day")
def make_day(target_day="cur"):
    make_day_helper(False, force_day=target_day)


def get_cookie():
    fn = os.path.join(os.environ['USERPROFILE'], "cookie.txt")
    if not os.path.isfile(fn):
        print("ERROR: Need '" + fn + "' with the session information!")
        raise Exception("Need cookie file!")

    with open(fn) as f:
        return f.read().strip()


def make_day_helper(offline, force_day=None):
    if not offline:
        get_cookie()

    for cur in os.listdir("Puzzles"):
        if "DO_NOT_CHECK_THIS_FILE_IN" in cur:
            raise Exception("You appear to be trying to rerun make_day before a day is done!")

    if force_day is None or force_day.lower() == "cur":
        helper_day = 1
        while os.path.isfile(os.path.join("Helpers", "day_%02d.py" % (helper_day,))):
            helper_day += 1
    else:
        helper_day = int(force_day)

    files = [
        os.path.join("Puzzles", "day_%02d_input.txt" % (helper_day,)),
        os.path.join("Helpers", "day_%02d.py" % (helper_day,)),
        os.path.join("Puzzles", "day_%02d.html" % (helper_day,)),
        os.path.join("Puzzles", "day_%02d.html.DO_NOT_CHECK_THIS_FILE_IN" % (helper_day,)),
    ]

    for filename in files:
        if os.path.isfile(filename):
            print("ERROR: '%s' already exists!" % (filename,))
            return

    todo = "TODO"
    for pass_number in range(2):
        if pass_number == 1:
            todo = dl_day(str(helper_day))

        with open(os.path.join("Helpers", "example.txt")) as f_src:
            with open(os.path.join("Helpers", "day_%02d.py" % (helper_day,)), "w") as f_dest:
                data = f_src.read()
                data = data.replace("DAY0_NUM", "%02d" % (helper_day,))
                data = data.replace("DAY_NUM", "%d" % (helper_day,))
                data = data.replace("DAY_TODO", todo)
                f_dest.write(data)

    with open(os.path.join("Puzzles", "day_%02d.html.DO_NOT_CHECK_THIS_FILE_IN" % (helper_day,)), "w") as f:
        f.write("You need to rerun dl_day!")

    if not offline:
        for filename in files:
            add_file(filename)

        for filename in files:
            if "html" not in filename:
                cmd = ["code", filename]
                if os.name == 'nt':
                    cmd = ["cmd", "/c"] + cmd
                subprocess.check_call(cmd)

    print("Created day #%d" % (helper_day,))


@opt("Show days")
def show_days():
    for helper in utils.get_helpers():
        print(helper.get_desc()[1])


def get_helpers_id(helper_day):
    helper_day = helper_day.lower()
    if helper_day == "all":
        for helper in utils.get_helpers():
            yield helper
    else:
        valid = set()
        def parse_value(value):
            if value.lower() in {"last", "latest", "cur", "now"}:
                last = None
                for helper in utils.get_helpers():
                    last = helper.get_desc()[0]
                return last
            else:
                return int(value)

        for part in helper_day.split(","):
            if "-" in part:
                part = part.split("-")
                for x in range(parse_value(part[0]), parse_value(part[1]) + 1):
                    valid.add(x)
            else:
                valid.add(parse_value(part))

        for helper in utils.get_helpers():
            if helper.get_desc()[0] in valid:
                yield helper


@opt("Test helper")
def test(helper_day):
    good = 0
    bad = 0

    sys.path.insert(0, 'Helpers')

    for helper in get_helpers_id(helper_day):
        print("## %s" % (helper.get_desc()[1]))
        try:
            resp = helper.test(Logger())
            if resp is not None and resp == False:
                raise ValueError("Returned false")
            print("That worked!")
            good += 1
        except ValueError:
            print("FAILURE!")
            bad += 1

    if good + bad > 1:
        print("# " + "-" * 60)

    print("Done, %d worked, %d failed" % (good, bad))
    if bad != 0:
        print("THERE WERE PROBLEMS")


_print_catcher = None
class PrintCatcher:
    def __init__(self):
        self.safe = False
        self.old_stdout = sys.stdout
        self.raw_used = False
        sys.stdout = self

    def write(self, value):
        if not self.safe:
            self.raw_used = True
        self.old_stdout.write(value)

    def flush(self):
        self.old_stdout.flush()

    def undo(self):
        sys.stdout = self.old_stdout
        return None


@opt("Run and time duration")
def run_time(helper_day):
    start = datetime.utcnow()
    run(helper_day)
    end = datetime.utcnow()
    safe_print("Done, that took %0.2f seconds" % ((end - start).total_seconds()))


@opt("Run helper")
def run(helper_day):
    global _print_catcher
    _print_catcher = PrintCatcher()
    run_helper(helper_day, False)
    if _print_catcher.raw_used:
        safe_print("WARNING: Raw 'print' used somewhere!")
    _print_catcher = _print_catcher.undo() # pylint: disable=assignment-from-none


@opt("Run helper and save output as correct")
def run_save(helper_day):
    run_helper(helper_day, True)


def safe_print(value):
    global _print_catcher
    if _print_catcher is not None:
        _print_catcher.safe = True
    print(value)
    if _print_catcher is not None:
        _print_catcher.safe = False


def run_helper(helper_day, save):
    sys.path.insert(0, 'Helpers')

    passed = 0
    failed = []

    for helper in get_helpers_id(helper_day):
        safe_print("## %s" % (helper.get_desc()[1]))
        with open(get_input_file(helper)) as f:
            values = []
            for cur in f:
                values.append(cur.strip("\r\n"))
        log = Logger()
        start = datetime.utcnow()
        helper.run(log, values)
        finish = datetime.utcnow()
        safe_print("# That took %.4f seconds to complete" % ((finish - start).total_seconds(),))
        filename = get_input_file(helper, file_type="expect")
        if save:
            if os.path.isfile(filename):
                edit_file(filename)
                log.save_to_file(filename)
            else:
                log.save_to_file(filename)
                add_file(filename)
        else:
            if os.path.isfile(filename):
                if log.compare_to_file(filename):
                    safe_print("# Got expected output!")
                    passed += 1
                else:
                    safe_print("# ERROR: Expected output doesn't match!")
                    failed.append("## %s FAILED!" % (helper.get_desc()[1]))
            else:
                safe_print("# No expected output to check")

    if passed + len(failed) > 1:
        safe_print("# " + "-" * 60)
        safe_print("Passed: %d" % (passed,))
        if len(failed) > 0:
            safe_print("ERROR: Failed: %d" % (len(failed),))
            for cur in failed:
                safe_print(cur)


@opt("Make a stand alone version of the day")
def make_demo(helper_day):
    sys.path.insert(0, 'Helpers')

    blanks = 0
    for helper in get_helpers_id(helper_day):
        filename = os.path.join("Helpers", "day_%02d.py" % (helper.get_desc()[0],))
        with open(filename) as f:
            for cur in f:
                cur = cur.strip("\r\n")
                print(cur)
                if cur.strip() == "":
                    blanks += 1
                else:
                    blanks = 0

        while blanks < 2:
            print("")
            blanks += 1

        print('# These are the simple versions of a more complex harness')
        print('')
        print('class Logger:')
        print('    def __init__(self):')
        print('        pass')
        print('')
        print('    def show(self, value):')
        print('        print(value)')
        print('')
        print('')
        print('def main():')
        print('    import os')
        print('    import sys')
        print('    if (sys.version_info.major, sys.version_info.minor) != (2, 7):')
        print('        print("WARNING: I expect to run on Python 2.7, no clue what\'s about to happen!")')
        print('    filename = "day_%02d_input.txt" % (get_desc()[0],)')
        print('    if not os.path.isfile(filename):')
        print('        print("ERROR: Need \'%s\' puzzle input to continue" % (filename,))')
        print('        return')
        print('    with open(filename) as f:')
        print('        values = []')
        print('        for line in f:')
        print('            values.append(line.strip("\\r\\n"))')
        print('    print("## Running \'%s\'..." % (get_desc()[1],))')
        print('    run(Logger(), values)')
        print('    print("All done!")')
        print('')
        print('')
        print('if __name__ == "__main__":')
        print('    main()')
        print('')


def get_header_footer():
    header = textwrap.dedent("""
        <!DOCTYPE html>
        <html lang="en-us">
        <head>
        <meta charset="utf-8"/>
        <title>Advent of Code """ + YEAR_NUMBER + """</title>
        <!--[if lt IE 9]><script src="html5.js"></script><![endif]-->
        <link href='SourceCodePro.css' rel='stylesheet' type='text/css'>
        <link rel="stylesheet" type="text/css" href="style.css"/>
        <link rel="stylesheet alternate" type="text/css" href="highcontrast.css?0" title="High Contrast"/>
        <link rel="shortcut icon" href="favicon.png"/>
        </head><body>
        <main>
    """).strip()

    footer = """</main></body></html>"""

    return header, footer


def get_page(url):
    import urllib.request
    cookie = get_cookie()

    req = urllib.request.Request(
        url, 
        headers={'Cookie': cookie},
    )
    resp = urllib.request.urlopen(req)
    resp = resp.read().decode("utf-8")
    resp = resp.encode('ascii', 'xmlcharrefreplace')
    resp = resp.decode("utf-8")
    return resp


@opt("Download Index")
def get_index():
    resp = get_page("https://adventofcode.com/%s" % (YEAR_NUMBER,))

    resp = re.sub("^.*<main>", "", resp, flags=re.DOTALL)
    resp = re.sub("</main>.*$", "", resp, flags=re.DOTALL)

    for i in range(30, 0, -1):
        resp = resp.replace("/%s/day/%d" % (YEAR_NUMBER, i), "day_%02d.html" % (i,))

    header, footer = get_header_footer()

    edit_file(os.path.join("Puzzles", "index.html"))

    with open(os.path.join("Puzzles", "index.html"), "wt", encoding="utf-8") as f:
        f.write(header + resp + footer)

    print("Wrote out index")


@opt("Download Day")
def dl_day(helper_day):
    ret = ""
    already_downloaded = False

    for helper in get_helpers_id(helper_day):
        if already_downloaded:
            time.sleep(0.250)
        already_downloaded = True
        helper_day = helper.get_desc()[0]

        bad_file = os.path.join("Puzzles", "day_%02d.html.DO_NOT_CHECK_THIS_FILE_IN" % (helper_day,))
        if os.path.isfile(bad_file):
            os.unlink(bad_file)
            revert_file(bad_file)

        filename = os.path.join("Puzzles", "day_%02d_input.txt" % (helper_day,))
        if not os.path.isfile(filename):
            resp = get_page("https://adventofcode.com/%s/day/%d/input" % (YEAR_NUMBER, helper_day))

            with open(filename, "wt", encoding="utf-8") as f:
                f.write(resp)

            print("Wrote out puzzle input for day #%d" % (helper_day,))

        resp = get_page("https://adventofcode.com/%s/day/%d" % (YEAR_NUMBER, helper_day))

        resp = re.sub("^.*<main>", "", resp, flags=re.DOTALL)
        resp = re.sub("</main>.*$", "", resp, flags=re.DOTALL)
        resp = re.sub('<p>At this point, you should <a href="/[0-9]+">return to your advent calendar</a> and try another puzzle.</p>.+', "", resp, flags=(re.MULTILINE | re.DOTALL))

        header, footer = get_header_footer()

        with open(os.path.join("Puzzles", "day_%02d.html" % (helper_day,)), "wt", encoding="utf-8") as f:
            f.write(header + resp + footer)

        print("Wrote out puzzle for day #%d" % (helper_day,))

        m = re.search("<h2>--- (.*?) ---</h2>", resp)
        if m:
            ret = m.group(1)
            ret = ret.replace("&gt;", ">")
            ret = ret.replace("&lt;", "<")
            ret = ret.replace("&amp;", "&")

    return ret


if __name__ == "__main__":
    main_entry('func', program_desc=DESC)

