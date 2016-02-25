from gocept.jenkinsdsl.jenkinsdsl import Handler, InterpolatableConfigParser
import pytest


CAUTION = '// *Caution:* Do not change'
VCS_INTERFACE = 'interface VersionControlSystem {}'
HG_CLASS = 'class HG implements VersionControlSystem {'
SVN_CLASS = 'class SVN implements VersionControlSystem {'
ABSTRACTBUILDER_CLASS = 'class AbstractBuilder implements Builder {'
PYTESTBUILDER_CLASS = 'class PytestBuilder extends AbstractBuilder {'
CUSTOMBUILDER_CLASS = 'class CustomBuilder extends AbstractBuilder {'
JOB_CONFIG = 'class JobConfig {'
COPY_NEXT_LINE = 'COPY NEXT LINE MANUALLY TO POST-BUILD-ACTIONS'
REDMINE_CLASS = 'class Redmine {'
NEW_JOBCONFIG = 'new JobConfig'


@pytest.fixture('function')
def config(tmpdir):
    """Create a config file with the given content."""
    def config(content):
        data = tmpdir.join('config.ini')
        data.write(content)
        return data.open()
    return config


def extract_string(string, text, start):
    """Extract a substring of `text` starting with `start` and with the
       same length as `string`."""
    idx_start = text.find(start)
    return text[idx_start:idx_start+len(string)]


def test_jenkinsdsl__Handler____call____1(config):
    """It returns a complete groovy dsl template."""
    config_file = config(r"""
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
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert VCS_INTERFACE in result
    assert HG_CLASS in result
    assert ABSTRACTBUILDER_CLASS in result
    assert PYTESTBUILDER_CLASS in result
    assert JOB_CONFIG in result
    assert COPY_NEXT_LINE in result
    assert REDMINE_CLASS in result

    expected_jobconfig = (
        r"new JobConfig(name: 'gocept.jenkinsdsl', "
        r"vcs: new HG(name: 'gocept.jenkinsdsl', "
        r"baseurl: 'https://bitbucket.org', group: 'gocept'), "
        r"builder: new PytestBuilder(timeout: '40', "
        r"base_commands: '\\$PYTHON_EXE bootstrap.py\\nbin/buildout', "
        r"additional_commands: 'bin/test'), "
        r"redmine: new Redmine(website_name: 'gocept', "
        r"project_name: 'gocept.jenkinsdsl'))")
    assert expected_jobconfig == extract_string(
        expected_jobconfig, result, NEW_JOBCONFIG)


def test_jenkinsdsl__Handler____call____2(config):
    """It does not render specific snippets if there params are not set."""
    config_file = config(r"""
[gocept.jenkinsdsl]
foo = bar
""")
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert VCS_INTERFACE in result
    assert HG_CLASS not in result
    assert ABSTRACTBUILDER_CLASS not in result
    assert PYTESTBUILDER_CLASS not in result
    assert JOB_CONFIG in result
    assert COPY_NEXT_LINE in result
    assert REDMINE_CLASS not in result


def test_jenkinsdsl__Handler____call____3(config):
    """It does not render specific snippets twice if having > 1 job."""
    config_file = config(r"""
[gocept.jenkinsdsl]
vcs = hg
builder = pytest

[gocept.testing]
vcs = hg
builder = pytest
""")
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert 1 == result.count(HG_CLASS)
    assert 1 == result.count(ABSTRACTBUILDER_CLASS)
    assert 1 == result.count(PYTESTBUILDER_CLASS)
    assert 1 == result.count(JOB_CONFIG)
    assert 2 == result.count(NEW_JOBCONFIG)


def test_jenkinsdsl__Handler____call____4(config):
    """It supports SVN and a custom builder."""
    config_file = config(r"""
[gocept.jenkinsdsl]
vcs = svn
svn_baseurl = http://base.url
svn_group = gocept
svn_credentials = <UUID>
svn_realm = <REALM>
svn_scm_browser = hudson.plugins.redmine.RedmineRepositoryBrowser
builder = custom
""")
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert VCS_INTERFACE in result
    assert SVN_CLASS in result
    assert ABSTRACTBUILDER_CLASS in result
    assert CUSTOMBUILDER_CLASS in result
    assert ("new SVN(name: 'gocept.jenkinsdsl', baseurl: 'http://base.url'" in
            result)


def test_jenkinsdsl__Handler____call____5(config):
    """It supports interpolation within a section value."""
    config_file = config(r"""
[gocept.jenkinsdsl]
vcs = hg
builder = pytest
test_options = --junitxml=junit.xml
pytest_base_commands =
    bin/test {test_options}
not_included_field =
    this_will_be_not_included
""")
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert VCS_INTERFACE in result
    assert HG_CLASS in result
    assert 'bin/test --junitxml=junit.xml' in result
    assert 'not_included_field' not in result
    assert 'this_will_be_not_included' not in result


def test_jenkinsdsl__Handler____call____6(config):
    """It supports interpolation within a section value with chained ...

    ... interpolations."""
    config_file = config(r"""
[gocept.jenkinsdsl]
vcs = hg
builder = pytest
coverage_options = -cov src
test_options = --junitxml=junit.xml {coverage_options}
pytest_base_commands =
    bin/test {test_options}
""")
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert VCS_INTERFACE in result
    assert HG_CLASS in result
    assert 'bin/test --junitxml=junit.xml -cov src' in result


def test_jenkinsdsl__Handler____call____7(config):
    """It supports interpolation within a section value with chained ...

    ... interpolations and goes not into recursive loops."""
    config_file = config(r"""
[gocept.jenkinsdsl]
vcs = hg
builder = pytest
coverage_options = -cov src {test_options}
test_options = --junitxml=junit.xml {coverage_options}
pytest_base_commands =
    bin/test {test_options}
""")
    result = Handler(config_file)()
    assert result.startswith(CAUTION)
    assert VCS_INTERFACE in result
    assert HG_CLASS in result
    expected_options = ('bin/test --junitxml=junit.xml -cov src '
                        '--junitxml=junit.xml {coverage_options}')
    assert expected_options == extract_string(
        expected_options, result, 'bin/test')


def test_jenkinsdsl__InterpolatableConfigParser__interpolate_section_values_1(
        config):
    """It supports the interpolation in a deterministic order, when the ...

    ... the snippets are chained, even when a loop would occur."""
    config_file_1 = (r"""
[gocept.jenkinsdsl]
vcs = hg
builder = pytest
coverage_options = -cov src
test_options = --junitxml=junit.xml {coverage_options}
pytest_base_commands =
    bin/test {test_options}
""")
    inter_config = InterpolatableConfigParser()
    inter_config.read_string(config_file_1)
    inter_config.interpolate_section_values()
    assert '--junitxml=junit.xml -cov src' == inter_config[
        'gocept.jenkinsdsl']['test_options']
    assert '\nbin/test --junitxml=junit.xml -cov src' == inter_config[
        'gocept.jenkinsdsl']['pytest_base_commands']

    config_file_2 = (r"""
[gocept.jenkinsdsl]
vcs = hg
builder = pytest
coverage_options = -cov src {test_options}
test_options = --junitxml=junit.xml {coverage_options}
pytest_base_commands =
    bin/test {test_options}
""")
    inter_config = InterpolatableConfigParser()
    inter_config.read_string(config_file_2)
    inter_config.interpolate_section_values()
    assert '-cov src --junitxml=junit.xml {coverage_options}' == inter_config[
        'gocept.jenkinsdsl']['coverage_options']
    assert ('\nbin/test --junitxml=junit.xml '
            '-cov src --junitxml=junit.xml {coverage_options}') == (
            inter_config['gocept.jenkinsdsl']['pytest_base_commands'])
