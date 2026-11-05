#!/usr/bin/env python3
"""Package the oldest compatible binaries into one ZIP per ABI and OS."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


SHARED_FILES = (
    'configs/ripext/ca-bundle.crt',
    'scripting/include/ripext.inc',
    'scripting/include/ripext/http.inc',
    'scripting/include/ripext/json.inc',
)
PREFIX = Path('addons/sourcemod')


def package(artifacts, output, version):
    # Validate every input before producing any archives.
    archives = []
    for platform, suffix in (('Linux', 'so'), ('Windows', 'dll')):
        binary = 'rip.ext.' + suffix
        for group, x86_sdk, x64_sdk in (
            ('sm1.7-1.12', '1.7-dev', '1.10-dev'),
            ('sm1.13', 'master', 'master'),
        ):
            x86 = artifacts / (platform + '-' + x86_sdk)
            x64 = artifacts / (platform + '-' + x64_sdk)
            files = [(x86 / PREFIX / name, PREFIX / name) for name in SHARED_FILES]
            files += [
                (x86 / PREFIX / 'extensions' / binary, PREFIX / 'extensions' / binary),
                (x64 / PREFIX / 'extensions/x64' / binary, PREFIX / 'extensions/x64' / binary),
            ]
            for source, _ in files:
                if not source.is_file():
                    raise FileNotFoundError(source)
            name = 'sm-ripext-{}-{}-{}.zip'.format(version, group, platform.lower())
            archives.append((output / name, files))

    output.mkdir(parents=True, exist_ok=True)
    for path, files in archives:
        with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
            for source, destination in files:
                archive.write(source, destination.as_posix())
        print(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    package(args.artifacts, args.output, args.version)
