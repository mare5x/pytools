from pytools import httptools
from pytools import filetools
import logging
import concurrent.futures

# TEST_FILE_URL = "http://www.ovh.net/files/1Mio.dat"
# TEST_FILE_MD5 = "6cb91af4ed4c60c11613b75cd1fc6116"

TEST_FILE_URL = "http://www.ovh.net/files/10Mio.dat"
TEST_FILE_MD5 = "ecf2a421f46ab33f277fa2aaaf141780"

DST_DIR = "."

logging.basicConfig(filename="log.txt", level=logging.INFO)

def check(dst, checksum):
    assert filetools.md5sum(dst) == TEST_FILE_MD5
    filetools.remove_file(dst)

print("Range download available:", httptools.range_download_available(TEST_FILE_URL))
print("Content length:", httptools.get_content_length(TEST_FILE_URL))

dst = httptools.download_url(TEST_FILE_URL, DST_DIR)
check(dst, TEST_FILE_MD5)
dst = httptools.download_basic(TEST_FILE_URL, dir_path=DST_DIR, with_progress=True)
check(dst, TEST_FILE_MD5)
dst = httptools.download_multiple_connections(TEST_FILE_URL, DST_DIR, connections=5)
check(dst, TEST_FILE_MD5)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    futures = { ex.submit(httptools.download_basic, TEST_FILE_URL, dir_path=DST_DIR, file_name=str(i)) 
        for i in range(5) }
    for future in concurrent.futures.as_completed(futures):
        check(future.result(), TEST_FILE_MD5)
