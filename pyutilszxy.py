import os
import hashlib


# hign speed,recommended
# delete all dirs and file under directory dirpath
def delete_dirs_and_files(dirpath):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
        os.rmdir(root)


# hign speed,recommended
# traverse all files and return the absolute path
def walk_files(path, endpoint=None):
    file_list = []
    for root, dirs, files in os.walk(path):
        # print(root, "*" * 20, dirs, "*" * 20, files)
        for file in files:
            file_path = os.path.join(root, file)
            # if file_path.endswith(endpoint):
            file_list.append(file_path)

    return file_list


def makedirs(path, mode=0o777, ignore_errors=False, exist_ok=False):
    """
    Create a leaf directory and all intermediate ones.

    Based on os.makedirs, but also supports ignore_errors which will
    ignore all errors raised by os.makedirs.
    """
    if exist_ok and os.path.exists(path):
        return
    try:
        os.makedirs(path, mode)
        os.chmod(path, mode)
    except:
        if not ignore_errors:
            raise OSError('Create dir: {!r} error.'.format(path))


# md5hash the given string
def stringtomd5(originstr):
    return hashlib.md5(originstr.encode("utf-8")).hexdigest()


if __name__ == '__main__':
    wav_path = "nm/fca/1/crashes"
    text_list = walk_files(wav_path)
    print(text_list)
    delete_dirs_and_files("/home/kakaxdu/prjdataspell/onefuzzer/crashes_analysis_old")
    print(len(stringtomd5("jkfjklfkfasdfkjl;;;;;;;;;;;;;;;;;;;;;;;;as\nfdasl;kdddddddddddddddddddf\n")))
