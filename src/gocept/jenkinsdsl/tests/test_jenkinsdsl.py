from gocept.jenkinsdsl.jenkinsdsl import Handler


def test_jenkinsdsl__Handler____call____1(tmpdir):
    """It returns a complete groovy dsl template."""
    config_file = tmpdir.join('config.ini')
    config_file.write(r"""
[DEFAULT]
hg_baseurl = https://bitbucket.org
hg_group = gocept

builder = pytest
pytest_timeout = 40
pytest_base_commands =
    \$PYTHON_EXE bootstrap.py
    bin/buildout
pytest_additional_commands =
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

    expected_jobconfig = r"new JobConfig(name: 'gocept.jenkinsdsl', vcs: new HG(name: 'gocept.jenkinsdsl', baseurl: 'https://bitbucket.org', group: 'gocept'), builder: new PytestBuilder(timeout: '40', base_commands: '\\$PYTHON_EXE bootstrap.py\\nbin/buildout', additional_commands: 'bin/test'), redmine: new Redmine(website_name: 'gocept', project_name: 'gocept.jenkinsdsl'))"
    begin_jobconfig = result.find('new JobConfig')
    result_jobconfig = result[begin_jobconfig: begin_jobconfig + len(expected_jobconfig)]
    assert expected_jobconfig == result_jobconfig

