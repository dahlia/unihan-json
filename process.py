#!/usr/bin/env python3.6
import json
import logging
import pathlib
import re
import sys
import tempfile
from typing import (Callable, Dict, Iterator, List, Mapping,
                    Match, Pattern, Tuple)

__all__ = ('UNICODE_POINT_RE', 'PROP_PARSERS', 'PropWriter',
           'main', 'parse_unicode_point', 'parse_unicode_points')


UNICODE_POINT_RE: Pattern = re.compile('^U\+([0-9A-Fa-f]+)$')


def parse_unicode_point(unicode_point: str) -> str:
    m: Match = UNICODE_POINT_RE.match(unicode_point)
    if not m:
        raise ValueError(f'invalid unicode point: {unicode_point!r}')
    return chr(int(m.group(1), 16))


def parse_unicode_points(unicode_points: str) -> List[str]:
    try:
        return [parse_unicode_point(code) for code in unicode_points.split()]
    except ValueError:
        raise ValueError(f'invalid unicode points: {unicode_points!r}')


def parse_hangul(entries: str) -> Dict[str, str]:
    return dict(pair.split(':', 1) for pair in entries.split())


HANYU_PINLU_RE: Pattern = re.compile(
    '^([^()]+)[(]([0-9]+)[)]$'
)


def parse_hanyu_pinlu(entries: str) -> Dict[str, int]:
    m = HANYU_PINLU_RE.match
    return {
        reading: int(freq)
        for entry in entries.split()
        for (reading, freq) in (m(entry).groups(),)
    }


def parse_hanyu_pinyin(entries: str) -> Dict[str, List[str]]:
    return {
        entry_num: readings.split(',')
        for entry in entries.split()
        for (entry_num, readings) in (entry.split(':', 1),)
    }


def parse_ints(entries: str) -> List[int]:
    return [int(entry) for entry in entries.split()]


PROP_PARSERS: Mapping[str, Callable[[str], object]] = {
    # CHECK: When a parser is added, update README.md as well.
    'kAccountingNumeric': int,
    'kCantonese': str.split,
    'kFrequency': int,
    'kGB0': int,
    'kGB1': int,
    'kGB3': int,
    'kGB5': int,
    'kGB7': int,
    'kGB8': int,
    'kGradeLevel': int,
    'kHangul': parse_hangul,
    'kHanyuPinlu': parse_hanyu_pinlu,
    'kHanyuPinyin': parse_hanyu_pinyin,
    'kJapaneseKun': str.split,
    'kJapaneseOn': str.split,
    'kLau': parse_ints,
    'kNelson': parse_ints,
    'kOtherNumeric': int,
    'kPrimaryNumeric': int,
    'kSimplifiedVariant': parse_unicode_points,
    'kTaiwanTelegraph': int,
    'kTang': str.split,
    'kTotalStrokes': parse_ints,
    'kTraditionalVariant': parse_unicode_points,
    'kVietnamese': str.split,
}


class PropWriter:

    DEFAULT_FILENAME_FORMAT: str = '{0}.json'

    def __init__(self,
                 directory_path: pathlib.Path,
                 filename_format: str=DEFAULT_FILENAME_FORMAT) -> None:
        self.directory_path = directory_path
        self.filename_format = filename_format
        self.temp_files = {}
        self.logger = logging.getLogger(
            f'{PropWriter.__module__}.{PropWriter.__qualname__}'
        )

    def __enter__(self) -> 'PropWriter':
        return self

    def __exit__(self, *exc_info) -> None:
        logger = self.logger
        for prop, file_path in self.flush():
            logger.info('%s: %s', prop, file_path)
        for prop, tf in self.temp_files.items():
            tf.close()

    def feed_file(self, file) -> None:
        for line in file:
            self.feed_line(line)

    def feed_line(self, line: str) -> None:
        ltrimmed = line.lstrip()
        if not ltrimmed or ltrimmed.startswith('#'):
            return
        try:
            code, prop, value = line.split('\t', 2)
        except ValueError as e:
            raise ValueError(f'{e}: {line!r}')
        try:
            f = self.temp_files[prop]
        except KeyError:
            f = tempfile.TemporaryFile(mode='w+', prefix=prop)
            self.temp_files[prop] = f
        print(line.rstrip('\r\n'), file=f)

    def flush(self) -> Iterator[Tuple[str, pathlib.Path]]:
        for prop, tf in self.temp_files.items():
            tf.flush()
            tf.seek(0)
            file_path = self.directory_path / self.filename_format.format(prop)
            yield prop, file_path
            parse_value = PROP_PARSERS.get(prop, str)
            with file_path.open('w') as f:
                wf = f.write
                wf('{')
                first = True
                for line in tf:
                    try:
                        code, prop, value = line.rstrip('\r\n').split('\t', 2)
                    except ValueError as e:
                        raise ValueError(f'{e}: {line!r}')
                    char = parse_unicode_point(code)
                    parsed_value = parse_value(value)
                    if first:
                        wf('\n')
                        first = False
                    else:
                        wf(',\n')
                    wf('\t')
                    wf(json.dumps(char, ensure_ascii=False))
                    wf(':')
                    wf(json.dumps(parsed_value, ensure_ascii=False))
                wf('\n}\n')


def main() -> None:
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} UNIHAN_DIR DEST_DIR', file=sys.stderr)
        raise SystemExit(2)
    data_dir_path = pathlib.Path(sys.argv[1])
    dest_dir_path = pathlib.Path(sys.argv[2])
    if not data_dir_path.is_dir():
        print(f'error: {data_dir_path} is not a directory')
        raise SystemExit(2)
    elif dest_dir_path.is_file():
        print(f'error: {dest_dir_path} already exists and is a file')
        raise SystemExit(2)
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format='%(message)s'
    )
    dest_dir_path.mkdir(parents=True, exist_ok=True)
    with PropWriter(dest_dir_path) as prop_writer:
        for data_path in data_dir_path.glob('*.txt'):
            print(data_path, file=sys.stderr)
            with data_path.open() as f:
                prop_writer.feed_file(f)


if __name__ == '__main__':
    main()
