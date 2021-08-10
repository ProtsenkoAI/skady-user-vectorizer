import os


def get_and_delete_last_file_line(file):
    # src: https://superuser.com/questions/127786/efficiently-remove-the-last-two-lines-of-an-extremely-large-text-file
    count = 0
    nb_lines = 1
    last_line = ""
    with open(file, 'r+b', buffering=0) as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            char = f.read(1)
            if char != b'\n' and f.tell() == end:
                # file does not end with a newline, so just exit
                return
            if char == b'\n':
                count += 1
            else:
                last_line = char.decode("utf-8") + last_line
            if count == nb_lines + 1:
                f.truncate()
                return last_line
            f.seek(-1, os.SEEK_CUR)
    return last_line


if __name__ == "__main__":
    # some unit_tests
    file_pth = "../../../resources/other/test_last_line.txt"
    print(get_and_delete_last_file_line(file_pth))
