from gocept.jenkinsdsl.jenkinsdsl import Handler


def test_jenkinsdsl__Handler____call____1(tmpdir):
    """It returns a complete groovy dsl template."""
    config_file = tmpdir.join('config.ini')
    config_file.write(r"""
[DEFAULT]
hg_baseurl = https://bitbucket.org
hg_group = gocept

builder = pytest
build_timeout = 40
build_base_command =
    \$PYTHON_EXE bootstrap.py
    bin/buildout
build_pytest_command =
    bin/test

[gocept.jenkinsdsl]
vcs = hg
builder = pytest
redmine_website_name = gocept
redmine_project_name = gocept.jenkinsdsl
""")
    h = Handler(config_file.open())
    result = h()

    assert result.startswith('// *Caution:* Do not change')
    assert 'interface VersionControlSystem {}' in result
    assert 'class HG implements VersionControlSystem {' in result
    assert 'class AbstractBuilder implements Builder {' in result
    assert 'class PytestBuilder extends AbstractBuilder {' in result
    assert 'class JobConfig {' in result
    assert 'COPY NEXT LINE MANUALLY TO POST-BUILD-ACTIONS' in result
    assert 'class Redmine {' in result
