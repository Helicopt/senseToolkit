import platform
import time
fcntl = None
msvcrt = None
bLinux = True
if platform.system() != 'Windows':
    fcntl = __import__("fcntl")
    bLinux = True
else:
    msvcrt = __import__('msvcrt')
    bLinux = False


class CFileLock:
    def __init__(self, filename):
        self.filename = filename + '.lock'
        self.file = None

    def lock(self, max_count=None):
        cnt = 0
        if bLinux is True:
            self.file = open(self.filename, 'wb')
            while True:
                try:
                    fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    # print(self.filename, ' file_lock success ********')
                    return True
                except:
                    # print(self.filename, ' file_lock error')
                    time.sleep(1)
                    cnt += 1
                    if max_count is not None and cnt > max_count:
                        return False
        else:
            self.file = open(self.filename, 'wb')
            while True:
                try:
                    msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
                    # print(self.filename, ' file_lock success ********')
                    return True
                except:
                    # print(self.filename, ' file_lock error')
                    time.sleep(1)
                    cnt += 1
                    if max_count is not None and cnt > max_count:
                        return False

    def unlock(self):
        try:
            if bLinux is True:
                fcntl.flock(self.file, fcntl.LOCK_UN)
                self.file.close()
            else:
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            return True
            # print(self.filename, ' file_unlock success')
        except:
            # print('file_unlock error')
            return False
