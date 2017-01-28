import requests
import os
from lxml import html
import logging
import concurrent.futures
from functools import wraps
import math

from .fileutils import *
from .cmdtools import *
from . import printer


CHUNK_SIZE = 2 ** 20  # 1 MiB


def downloading_log(func):
    wraps(func)
    def inner_log(*args, **kwargs):
        time_started = time.time()
        url = args[0]
        path = kwargs.get("path", "")
        logging.info('Downloading {url} to {path}'.format(url=url, path=path))
        result = func(*args, **kwargs)
        logging.info('Completed downloading {path} ({size}) (took {time} to finish)'.format(
                      path=path, size=get_file_size(path), time=format_seconds(time.time() - time_started)))
        return result
    return inner_log


def get_html_element(url, *args, **kwargs):
    r = requests.get(url, *args, **kwargs)
    return html.fromstring(r.text)


def download_url(url, path, *args, **kwargs):
    if range_download_available(url, *args, **kwargs):
        download_multiple_connections(url, path, *args, **kwargs)
    else:
        download_basic(url, path, *args, **kwargs)


def download_basic(url, *args, dir_path=".", file_name="", file_path="", with_progress=True, **kwargs):
    time_started = time.time()

    total = get_content_length(url, *args, **kwargs)
    total_str = convert_file_size(total)

    if not file_path:
        file_path = os.path.join(dir_path, file_name) if file_name else path_from_url(dir_path, url)

    logging.info('Downloading {url} to {path}'.format(url=url, path=file_path))

    r = requests.get(url, *args, stream=True, **kwargs)
    downloaded = 0
    with open(file_path, 'wb') as f, printer.printer() as pprint:
        if with_progress: chunk_time = time.time()
        for chunk in r.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if with_progress and total > 0:
                    pprint.print("{file_name} {progress} ({downloaded} / {total}) [{speed}]".format(
                        file_name=os.path.basename(file_path), 
                        progress=progress_bar(downloaded / total, time_started),
                        downloaded=convert_file_size(downloaded),
                        total=total_str,
                        speed=format_speed(chunk_time, len(chunk))))
                    chunk_time = time.time()
        if with_progress: pprint.print("Done with {file_path}".format(file_path=file_path))

        logging.info('Completed downloading {path} ({size}) (took {time} to finish)'.format(
                    path=file_path, size=total_str if total > 0 else get_file_size(file_path), time=format_seconds(time.time() - time_started)))


def range_download_available(url, *args, **kwargs):
    r = requests.head(url, *args, **kwargs)
    try:
        return r.headers['accept-ranges'] == 'bytes'
    except KeyError:
        headers = kwargs.pop('headers', {})
        headers['Range'] = 'bytes=0-0'
        r = requests.get(url, *args, headers=headers, **kwargs)
        return r.status_code == 206


def get_content_length(url, *args, **kwargs):
    r = requests.head(url, *args, **kwargs)
    content_length = int(r.headers.get('content-length', 0))
    if not content_length:
        headers = kwargs.pop('headers', {})
        headers['Range'] = 'bytes=0-0'
        r = requests.get(url, *args, headers=headers, **kwargs)
        if r.status_code == 206:
            # eg: 'content-range': 'bytes 0-0/10494470'
            content_length = int(r.headers['content-range'].rsplit('/')[1])
    return content_length


def download_multiple_connections(url, dir_path, *args, file_name="", connections=5, **kwargs):
    file_path = os.path.join(dir_path, file_name) if file_name else path_from_url(dir_path, url)
    
    logging.info('Downloading {url} to {path} with {connections} connections.'.format(url=url, path=file_path, connections=connections))

    total = get_content_length(url, *args, **kwargs)
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:
        b_range = math.ceil(total / connections)
        for i in range(connections):
            part_path = '{path}.part{part}'.format(path=file_path, part=i + 1)
            futures.append(executor.submit(download_byte_range, url, part_path, (i * b_range) + i, ((i + 1) * b_range) + i, *args, **kwargs))

    parts = [future.result() for future in futures]
    parts.sort()
    logging.info('Concatenating downloaded parts to {}'.format(file_path))
    join_files(file_path, parts)
    logging.info('Removing .part files for {}'.format(file_path))
    [remove_file(part) for part in parts]


def download_byte_range(url, path, start_range, end_range, *args, **kwargs):
    with open(path, 'wb') as f:
        headers = kwargs.pop('headers', {})
        headers['Range'] = "bytes={}-{}".format(start_range, end_range)

        r = requests.get(url, *args, stream=True, headers=headers, **kwargs)

        chunk_time = time.time()
        for chunk in r.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                print(format_speed(chunk_time, len(chunk)), end='\r')
                chunk_time = time.time()

    return path


def download_urls(urls, path, *args, threads=3, **kwargs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        if type(path) == str:
            executor.map(download_url, urls, [p for p in urls], *args, **kwargs)
        else:
            executor.map(download_url, urls, path, *args, **kwargs)


def path_from_url(dir_path, url, overwrite=True):
    dir_path = os.path.abspath(dir_path)
    create_dir(dir_path)
    return os.path.join(dir_path, os.path.basename(url)) if overwrite else create_filename(os.path.join(dir_path, os.path.basename(url)))


def threads(num_threads):
    def threaded_download(func):
        @wraps(func)
        def download(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result()
        return download
    return threaded_download

