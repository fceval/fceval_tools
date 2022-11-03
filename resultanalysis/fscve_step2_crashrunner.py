import argparse

from sqlalchemy import text

from fscve_step1_db import FscveStep1DbHelper
from pyutilszxy import makedirs
import pandas as pd
from pyutilszxy import stringtomd5
import linecache
from fscve_step1_db import CrashAnalysis
import sys
import subprocess
import re
import os
import time
import glob
import shlex
import shutil
import threading
from time import sleep
from pyutilszxy import walk_files

BIN2ARGS = {
    "addr2line": "-e @@",
    "ar": "-t @@",
    "strings": "-d @@",
    "size": "@@",
    "c++filt": "@@",
    # "nm-new": "-a -C -l --synthetic @@",
    # "nm": "-a -C -l --synthetic @@",
    # "nm": "-a -C -l --synthetic @@",
    "nm": " -C @@",
    # "objdump": "--dwarf-check -C -g -f -dwarf -x @@",
    "objdump": "-d @@",
    # "readelf": "-a -c -w -I @@",
    "readelf": "-a @@",
    # "strip-new": "-o /dev/null -s @@",
    "strip": "-o /dev/null -s @@",
    "xml": "@@",
    "gnuplot": "@@",
    "boringssl": "@@",
    "c-ares": "@@",
    "freetype2": "@@",
    "guetzli": "@@",
    "harfbuzz": "@@",
    "json": "@@",
    "lcms": "@@",
    "libarchive": "@@",
    "libjpeg-turbo": "@@",
    "libssh": "@@",
    "llvm-libcxxabi": "@@",
    "openssl-1.0.1f": "@@",
    "openssl-1.0.2d": "@@",
    "openssl-1.1.0c": "@@",
    "openssl-1.1.0c-bignum": "@@",
    "openssl-1.1.0c-x509": "@@",
    "openthread": "@@",
    "openthread-ip6": "@@",
    "openthread-radio": "@@",
    "pcre2": "@@",
    "proj4": "@@",
    "re2": "@@",
    "sqlite": "@@",
    "vorbis": "@@",
    "woff2": "@@",
    "wpantund": "@@",
    "base64": "-d @@",
    "md5sum": "-c @@",
    "uniq": "@@",
    "who": "@@",
    # zhaoxy add for unifuzz dataset start
    # zhaoxy add for unifuzz dataset start
    "cflow": "@@",
    "flvmeta": "@@",
    "infotocap": "-o /dev/null @@",
    "jhead": "@@",
    "jq": ". @@",
    "exiv2": "@@",
    "mp42aac": "@@ /dev/null",
    "wav2swf": "-o /dev/null @@",
    # "mp3gain": "@@"
    # zhaoxy add for unifuzz dataset end

    # zhaoxy add for putone mp3gain
    "mp3gain": "@@",
    # zhaoxy add for putonefile_magic
    "file_magic": "2147483647",
    "freetype2-2017": "@@",
    "file_magic_fuzzer": "@@",
    # zhaoxy add for magma
    "libpng": "@@",
    "libtiff": "@@",
    "libsndfile": "@@",
    "libxml2": "@@",
    "lua": "@@",
    "openssl": "@@",
    "as": "@@",
    "ld": "@@",
    "ranlib": "@@",
    "gprof": "@@",
}

# print(f"{BIN2ARGS['nm']}")
# para = BIN2ARGS[benchmark]
# cmd = f"./benchmarks/{benchmark} {para}"

# print(cmd)


"""
Assume that we have conducted experiments with 30 repetitions and the folder is like:
objdump/fca/1/crashes
We can run the crash to obtain ASAN output to folder objdump/fca/1/crashes
crashrunner.py
"""

MAX_THREADS = 6
os.environ[
    "ASAN_OPTIONS"] = 'stack_trace_format="FUNCTIONSTART%fFUNCTIONEND----LOCATIONSTART%SLOCATIONEND----FRAMESTART%nFRAMEEND"'
os.environ[
    "MSAN_OPTIONS"] = 'stack_trace_format="FUNCTIONSTART%fFUNCTIONEND----LOCATIONSTART%SLOCATIONEND----FRAMESTART%nFRAMEEND"'
os.environ[
    "TSAN_OPTIONS"] = 'stack_trace_format="FUNCTIONSTART%fFUNCTIONEND----LOCATIONSTART%SLOCATIONEND----FRAMESTART%nFRAMEEND"'
os.environ[
    "UBSAN_OPTIONS"] = 'stack_trace_format="FUNCTIONSTART%fFUNCTIONEND----LOCATIONSTART%SLOCATIONEND----FRAMESTART%nFRAMEEND"'
FINISHED = 0
RESULT = {}
output_folder = ""

# use the following environment variable
# os.environ["ASAN_SYMBOLIZER_PATH"] = 'ASAN_SYMBOLIZER_PATH= /usr/bin/llvm-symbolizer'

# hign speed,recommended
# delete all dirs and file under directory dirpath
def delete_dirs_and_files(dirpath):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
        os.rmdir(root)


def dprint(*args):
    sys.stderr.write(" ".join([str(i) for i in args]) + "\n")


def run_one_file(sanitizer, curfile, cmd, tmpfile, stdoutfile, stderrfile, timeoutfile, timeout=10):
    """
    Run certain file to get stdoutfile and stderrfile
    First, the file will be copied to tmpfile,
    then @@ in cmd will be replaced to tmpfile,
    output will be saved to stdoutfile and stderrfile
    if timedout, timeoutfile will be created

    Return: (nottimeout, runtime, outputtext)

    The caller should keep tmpfile only operated by current thread,
    stdoutfile folder should be present
    """
    global FINISHED
    shutil.copy(curfile, tmpfile)
    dprint(f"{sanitizer}-----{FINISHED}--------",curfile)
    if "@@" in cmd:
        cmds = shlex.split(cmd.replace("@@", tmpfile))
        stdin = None
    else:
        cmds = shlex.split(cmd)
        stdin = open(tmpfile, "rb")

    nottimeout = True
    exitcode = -15
    if os.path.exists(timeoutfile):
        os.unlink(timeoutfile)
    starttime = time.time()

    #dprint(cmds)
    try:
        x = subprocess.run(cmds, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        exitcode = x.returncode
    except subprocess.TimeoutExpired as e:
        x = e
        nottimeout = False
        with open(timeoutfile, "w") as tmp:
            tmp.write(curfile + "\n")
        exitcode = -15  # SIGTERM

    endtime = time.time()
    runtime = endtime - starttime
    if x.stdout is None or x.stderr is None:
        return nottimeout, exitcode, runtime, "empty outputtext"

    outputtext = x.stdout.decode(errors="ignore") + "\n" + x.stderr.decode(errors="ignore")

    with open(stdoutfile, "wb") as fp:
        fp.write(x.stdout)
    with open(stderrfile, "wb") as fp:
        fp.write(x.stderr)
    with open(stdoutfile.replace(".stdout", ".returncode"), "w") as fp:
        fp.write(str(exitcode))

    return nottimeout, exitcode, runtime, outputtext





def thread_main(files, cmd, threadid, myname, sanitizer):
    # in each thread, iteratively call run_one_file:
    #     run_one_file(file, cmd, tmpfile, stdoutfile, stderrfile, timeoutfile, timeout=10)
    # tmpfile is calculated using myname and threadid
    # pathname of other output files are generated using file pathname,
    # appending ".stdout", ".stderr", ".timeout" suffix respectively

    global FINISHED, RESULT, output_folder
    pwd = os.getcwd()
    len_files = len(files)
    for i in range(0, len_files):
    
        # we will place output files to a folder under crash_ananlysis
        # this folder is generated solely from file pathname
        # used as a cache folder, to speed up further analysis
        # we ignore certain keywords to shorten output_folder name
        curfile = files[i]
        # # print(file)
        fnames = curfile.split("/")
        fname = fnames[-1]

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        tmpfile = "{myname}_{threadid}".format(**locals())
        stdoutfile = output_folder + fname + ".stdout"
        stderrfile = output_folder + fname + ".stderr"
        timeoutfile = output_folder + fname + ".timeout"

        # res: (nottimeout, exitcode, runtime, outputtext)
        # do not read cache, run it!
        res = run_one_file(sanitizer, curfile, cmd, tmpfile, stdoutfile, stderrfile, timeoutfile, timeout=10)

        # print("zxy crash cmd result", res)
        RESULT[curfile] = res
        # if "AddressSanitizer" in res[3]:
        #     print(file)
        FINISHED += 1


def exec_crash_testcase_and_save_result(sanitizer):
    global output_folder,FINISHED
    FINISHED = 0
    wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    FILES = walk_files(wav_path)
    FILES = sorted(FILES)
    if not FILES:
        print("[Error] empty crash files? please check glob syntax!")
        dprint("Total files:0")
        # exit(1)
        return

    len_FILES = len(FILES)
    dprint("Total files:", len_FILES)

    # cmd = os.environ.get("CMD", None)
    # if not cmd:
    #     print("[Error] env CMD not given")
    #     exit(1)
    # cmd = f"./benchmarks/{benchmark} {BIN2ARGS[{benchmark}]}"
    para = BIN2ARGS[benchmark]
    cmd = f"./benchmarks/{sanitizer}/{benchmark} {para}"
    progpath = shlex.split(cmd)[0]
    print(progpath)
    progname = progpath.split("/")[-1]
    print(progname)

    assert os.access(progpath, os.X_OK), "CMD program not executable?"

    myname = f"tmp{sanitizer}/tmp_crashrunner_" + str(os.getpid())

    threadN = min(MAX_THREADS, len_FILES)

    for i in range(threadN):
        t = threading.Thread(target=thread_main, args=[FILES[i::threadN], cmd, i, myname, sanitizer])
        t.start()

    while FINISHED < len_FILES:
        dprint(sanitizer, "finished:", FINISHED, "/", len_FILES)
        sleep(2)

    foundbugids = set()
    for name, value in RESULT.items():
        text = value[3]
        print(name, "*" * 30, text)
        # if "AddressSanitizer" in text:
        #     foundbugids.add(getbugid(text, progname))
    dprint("bugids:", sorted(list(foundbugids)))

    for f in glob.glob(myname + "*"):
        os.unlink(f)


# fetch all crash files and save the vulerability to database table:crashs
def analysis_crash_exec_result():
    global RESULT

    wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    analysis_path = os.getcwd() + "/crashes_analysis/"
    FILES = walk_files(wav_path)
    if not FILES:
        print("[Error] empty crash files? please check glob syntax!")
        return
    test_case_hashes = [f.split("/")[-1] for f in FILES]
    for f in FILES:
        if RESULT[f][1] != 0 and RESULT[f][0] != 0:  # real bug #[1]exitcode,[0]nottimeout
            try:
                lines = linecache.getlines("{}{}.stderr".format(analysis_path, f.split("/")[-1]))
                frame_start = 0
                type_index = 0
                frame_end = 0
                for i in range(0, len(lines)):
                    if lines[i].find(
                            "ERROR: AddressSanitizer") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        type_index = i
                    if lines[i].find(
                            "FRAMESTART0FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_start = i
                    if lines[i].find(
                            "FRAMESTART3FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_end = i
                        break
                bug_line = lines[type_index]
                bug_type = re.findall(r"ERROR: AddressSanitizer: ([-a-zA-Z]+)\b", bug_line)  # eg.stack-overflow
                if len(bug_type) == 0:  # for bug_type[0] out of bound
                    continue
                # write real bugs to db
                new_analysis = CrashAnalysis(test_case_hash=f.split("/")[-1], crash_type=bug_type[0],
                                             frames_hash=stringtomd5(
                                                 ''.join([lines[j] for j in range(frame_start, frame_end + 1)])))
                session.add(new_analysis)
                session.commit()
            except Exception as e:
                print(e)


# fetch all crash files and save the vulerability to database table:crashs
def analysis_crash_exec_result_asan():
    global RESULT
    print("analysis_crash_exec_result_asan")
    wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    analysis_path = os.getcwd() + f"/crashes_analysisasan/"
    FILES = walk_files(wav_path)
    if not FILES:
        print("[Error] empty crash files? please check glob syntax!")
        return
    test_case_hashes = [f.split("/")[-1] for f in FILES]
    for f in FILES:
        if RESULT[f][1] != 0 and RESULT[f][0] != 0:  # real bug #[1]exitcode,[0]nottimeout
            try:
                lines = linecache.getlines("{}{}.stderr".format(analysis_path, f.split("/")[-1]))
                frame_start = 0
                type_index = 0
                frame_end = 0
                for i in range(0, len(lines)):
                    if lines[i].find(
                            "ERROR: AddressSanitizer") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        type_index = i
                    if lines[i].find(
                            "FRAMESTART0FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_start = i
                    if lines[i].find(
                            "FRAMESTART3FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_end = i
                        break
                bug_line = lines[type_index]
                bug_type = re.findall(r"ERROR: AddressSanitizer: ([-a-zA-Z]+)\b", bug_line)  # eg.stack-overflow
                if len(bug_type) == 0:  # for bug_type[0] out of bound
                    continue
                # write real bugs to db
                new_analysis = CrashAnalysis(test_case_hash=f.split("/")[-1], crash_type=bug_type[0],
                                             frames_hash=stringtomd5(
                                                 ''.join([lines[j] for j in range(frame_start, frame_end + 1)])),
                                             sanitizer="asan"
                                             )

                session.add(new_analysis)
                session.commit()
            except Exception as e:
                print(e)


# fetch all crash files and save the vulerability to database table:crashs
def analysis_crash_exec_result_msan():
    global RESULT
    print("analysis_crash_exec_result_msan")
    wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    analysis_path = os.getcwd() + f"/crashes_analysismsan/"
    FILES = walk_files(wav_path)
    if not FILES:
        print("[Error] empty crash files? please check glob syntax!")
        return
    test_case_hashes = [f.split("/")[-1] for f in FILES]
    for f in FILES:
        if RESULT[f][1] != 0 and RESULT[f][0] != 0:  # real bug #[1]exitcode,[0]nottimeout
            try:
                lines = linecache.getlines("{}{}.stderr".format(analysis_path, f.split("/")[-1]))
                frame_start = 0
                type_index = 0
                frame_end = 0
                for i in range(0, len(lines)):
                    if lines[i].find(
                            "ERROR: MemorySanitizer") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        type_index = i
                    if lines[i].find(
                            "FRAMESTART0FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_start = i
                    if lines[i].find(
                            "FRAMESTART3FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_end = i
                        break
                bug_line = lines[type_index]
                bug_type = re.findall(r"ERROR: MemorySanitizer: ([-a-zA-Z]+)\b", bug_line)  # eg.stack-overflow
                if len(bug_type) == 0:  # for bug_type[0] out of bound
                    continue
                # write real bugs to db
                new_analysis = CrashAnalysis(test_case_hash=f.split("/")[-1], crash_type=bug_type[0],
                                             frames_hash=stringtomd5(
                                                 ''.join([lines[j] for j in range(frame_start, frame_end + 1)])),
                                             sanitizer="msan"
                                             )

                session.add(new_analysis)
                session.commit()
            except Exception as e:
                print(e)


# fetch all crash files and save the vulerability to database table:crashs
def analysis_crash_exec_result_tsan():
    global RESULT
    print("analysis_crash_exec_result_tsan")
    wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    analysis_path = os.getcwd() + f"/crashes_analysistsan/"
    FILES = walk_files(wav_path)
    if not FILES:
        print("[Error] empty crash files? please check glob syntax!")
        return
    test_case_hashes = [f.split("/")[-1] for f in FILES]
    for f in FILES:
        if RESULT[f][1] != 0 and RESULT[f][0] != 0:  # real bug #[1]exitcode,[0]nottimeout
            try:
                lines = linecache.getlines("{}{}.stderr".format(analysis_path, f.split("/")[-1]))
                frame_start = 0
                type_index = 0
                frame_end = 0
                for i in range(0, len(lines)):
                    if lines[i].find(
                            "ERROR: ThreadSanitizer") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        type_index = i
                    if lines[i].find(
                            "FRAMESTART0FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_start = i
                    if lines[i].find(
                            "FRAMESTART3FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_end = i
                        break
                bug_line = lines[type_index]
                bug_type = re.findall(r"ERROR: ThreadSanitizer: ([-a-zA-Z]+)\b", bug_line)  # eg.stack-overflow
                if len(bug_type) == 0:  # for bug_type[0] out of bound
                    continue
                # write real bugs to db
                new_analysis = CrashAnalysis(test_case_hash=f.split("/")[-1], crash_type=bug_type[0],
                                             frames_hash=stringtomd5(
                                                 ''.join([lines[j] for j in range(frame_start, frame_end + 1)])),
                                             sanitizer="tsan"
                                             )

                session.add(new_analysis)
                session.commit()
            except Exception as e:
                print(e)


# fetch all crash files and save the vulerability to database table:crashs
def analysis_crash_exec_result_ubsan():
    global RESULT
    print("analysis_crash_exec_result_ubsan")
    wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    analysis_path = os.getcwd() + f"/crashes_analysisubsan/"
    FILES = walk_files(wav_path)
    if not FILES:
        print("[Error] empty crash files? please check glob syntax!")
        return
    test_case_hashes = [f.split("/")[-1] for f in FILES]
    for f in FILES:
        if RESULT[f][1] != 0 and RESULT[f][0] != 0:  # real bug #[1]exitcode,[0]nottimeout
            try:
                lines = linecache.getlines("{}{}.stderr".format(analysis_path, f.split("/")[-1]))
                frame_start = 0
                type_index = 0
                frame_end = 0
                for i in range(0, len(lines)):
                    if lines[i].find(
                            "ERROR: UndefinedBehaviorSanitizer") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        type_index = i
                    if lines[i].find(
                            "FRAMESTART0FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_start = i
                    if lines[i].find(
                            "FRAMESTART3FRAMEEND") != -1:  # fetch top 3 frames to decide the unique vulnerability
                        frame_end = i
                        break
                bug_line = lines[type_index]
                bug_type = re.findall(r"ERROR: UndefinedBehaviorSanitizer: ([-a-zA-Z]+)\b",
                                      bug_line)  # eg.stack-overflow
                if len(bug_type) == 0:  # for bug_type[0] out of bound
                    continue
                # write real bugs to db
                new_analysis = CrashAnalysis(test_case_hash=f.split("/")[-1], crash_type=bug_type[0],
                                             frames_hash=stringtomd5(
                                                 ''.join([lines[j] for j in range(frame_start, frame_end + 1)])),
                                             sanitizer="ubsan"
                                             )

                session.add(new_analysis)
                session.commit()
            except Exception as e:
                print(e)


def parse_args():
    parser = argparse.ArgumentParser(
        description="you should add those parameter benchmark--m fuzzer_combination--bm experiment_id---expid")
    parser.add_argument('--bm', help="benchmark name")
    parser.add_argument('--fc', help="fuzzer_combination name")
    parser.add_argument('--expid', help="experiment id")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    dbhelper = FscveStep1DbHelper(args.bm, args.fc, args.expid, False)
    session = dbhelper.session
    expid = dbhelper.experiment_id
    benchmark = dbhelper.benchmark
    fc = dbhelper.fc
    # query = session.query(AnalysisState.analysis_id,AnalysisState.discovery_id).first()
    # print(query)
    print(f"{benchmark}---{fc}-----{expid}")

    sans = {"asan", "tsan", "msan", "ubsan"}
    #sans = {"tsan"}  
    for san in sans:
        print(f"************running {san}*********************")
        shutil.rmtree(f"tmp{san}", ignore_errors=True)
        makedirs(f"tmp{san}", mode=0o777, ignore_errors=False, exist_ok=True)
        shutil.rmtree(f"crashes_analysis{san}", ignore_errors=True)
        makedirs(f"crashes_analysis{san}", mode=0o777, ignore_errors=False, exist_ok=True)
        output_folder = os.getcwd() + f"/crashes_analysis{san}/"
        if os.path.exists(output_folder):
            delete_dirs_and_files(output_folder)
        exec_crash_testcase_and_save_result(san)
        # drop table CrashAnalysis to store new data
    session.query(CrashAnalysis).delete()
    session.commit()
    analysis_crash_exec_result_asan()
    analysis_crash_exec_result_msan()
    analysis_crash_exec_result_tsan()
    analysis_crash_exec_result_ubsan()
    print("step2 crash runner end")
    print("************finished:fscve_step2_crashrunner*********************")
