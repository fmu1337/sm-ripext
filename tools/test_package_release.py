import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from package_release import PREFIX, SHARED_FILES, package


class PackageReleaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = self.root / 'artifacts'
        self.output = self.root / 'release'
        for platform, suffix in (('Linux', 'so'), ('Windows', 'dll')):
            for sdk in ('1.7-dev', '1.10-dev', 'master'):
                root = self.artifacts / (platform + '-' + sdk) / PREFIX
                names = list(SHARED_FILES) + [
                    'extensions/rip.ext.' + suffix,
                    'extensions/x64/rip.ext.' + suffix,
                    'unwanted-debug-file',
                ]
                for name in names:
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(platform + '/' + sdk + '/' + name)

    def test_four_archives_use_the_expected_baselines(self):
        package(self.artifacts, self.output, 'test')
        expected = {
            'sm-ripext-test-{}-{}.zip'.format(group, platform)
            for group in ('sm1.7-1.12', 'sm1.13')
            for platform in ('linux', 'windows')
        }
        self.assertEqual({p.name for p in self.output.iterdir()}, expected)
        for path in self.output.iterdir():
            platform = 'Linux' if path.stem.endswith('linux') else 'Windows'
            suffix = 'so' if platform == 'Linux' else 'dll'
            legacy = 'sm1.7-1.12' in path.name
            with ZipFile(path) as archive:
                self.assertEqual(set(archive.namelist()), {
                    (PREFIX / name).as_posix() for name in list(SHARED_FILES) + [
                        'extensions/rip.ext.' + suffix,
                        'extensions/x64/rip.ext.' + suffix,
                    ]
                })
                for directory, sdk in (
                    ('extensions', '1.7-dev' if legacy else 'master'),
                    ('extensions/x64', '1.10-dev' if legacy else 'master'),
                ):
                    member = (PREFIX / directory / ('rip.ext.' + suffix)).as_posix()
                    self.assertEqual(archive.read(member).decode(),
                                     platform + '/' + sdk + '/' + directory + '/rip.ext.' + suffix)

    def test_missing_baseline_does_not_publish_partial_archives(self):
        missing = self.artifacts / 'Windows-1.10-dev' / PREFIX / 'extensions/x64/rip.ext.dll'
        missing.unlink()
        with self.assertRaises(FileNotFoundError):
            package(self.artifacts, self.output, 'test')
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
