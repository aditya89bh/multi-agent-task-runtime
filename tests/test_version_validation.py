import pytest

from scripts.validate_version import read_project_version, validate_semver


def test_project_version_uses_semver():
    assert validate_semver(read_project_version()) == "0.1.0"


@pytest.mark.parametrize("version", ["1", "1.0", "v1.0.0", "1.0.0-beta", "01.0.0"])
def test_invalid_semver_is_rejected(version):
    with pytest.raises(ValueError):
        validate_semver(version)
