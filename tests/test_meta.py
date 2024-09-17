import ro_json
import re


def test_version():
    # The version shall be compatible with
    # packaging.version.Version
    # and enable comparison
    assert re.match(r'^\d+\.\d+\.\d+.*$', '1.2.3') is not None
    assert re.match(r'^\d+\.\d+\.\d+.*$', '1.2.3.post1') is not None
    assert re.match(r'^\d+\.\d+\.\d+.*$', '1.2.3.post13+g7cb3d69.dirty') is not None
    assert re.match(r'^\d+\.\d+\.\d+.*$', ro_json.__version__) is not None
