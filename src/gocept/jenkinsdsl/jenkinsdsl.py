import argparse
import pkg_resources
import re
import sys
import codecs
from io import StringIO
from configparser import ConfigParser
from collections import OrderedDict

parser = argparse.ArgumentParser(
    description='Generate DSL to generate Jenkins jobs.')
parser.add_argument('config', type=argparse.FileType('r'), help='Config file.')


class NestingError(Exception):
    """Raised when the maximum depth of nesting is reached."""

    def __init__(self, maximum_nested_depth):
        self.maximum_nested_depth = maximum_nested_depth

    def __str__(self):
        return repr(self.maximum_nested_depth)


class GroovyString(str):
    """Is a non interpolating groovy string with '''."""

    def __repr__(self):
        return "'''{}'''".format(self)

    def strip(self):
        return self.__class__(super().strip())

    def replace(self, *args, **kw):
        return self.__class__(super().replace(*args, **kw))


class GroovyExpression(GroovyString):
    """Is a rendered groovy expression."""

    def __repr__(self):
        return self.__str__()


class InterpolatableConfigParser(ConfigParser):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._nesting_count = 0
        self._maximum_nested_depth = 10
        reference_pattern = r"{\w+}"
        self._match_reference = re.compile(reference_pattern)

    def interpolate_section_values(self):
        for section in self.sections():
            section_params = self[section]
            self._maximum_nested_depth = int(section_params.get(
                'maximum_nested_depth', 10))
            for option, value in section_params.items():
                self._nesting_count = 0
                try:
                    self._interpolate_option(option, section_params)
                except NestingError as e:
                    print('For option `{}` a maximum nesting of {} was '
                          'reached'.format(option, e))
                    raise

    def _interpolate_option(self, option, params):
        if self._nesting_count >= self._maximum_nested_depth:
            raise NestingError(self._maximum_nested_depth)
        self._nesting_count += 1
        params[option] = params[option].format(**params)
        if self._match_reference.search(params[option]):
            self._interpolate_option(option, params)


class Handler(object):

    builder_class_map = {
        'pytest': 'PytestBuilder',
        'custom': 'CustomBuilder',
        'integration': 'IntegrationBuilder',
        'matrix': 'MatrixBuilder',
    }

    def __init__(self, config_file):
        self.config = InterpolatableConfigParser()
        self.config.read_file(config_file)
        self.config.interpolate_section_values()
        self.output = StringIO()
        self.required_templates = [
            'header.groovy',
            'interfaces.groovy',
            'jobconfig.groovy',
        ]

    def __call__(self):
        project_configs = [
            self._render_jobconfig(project_name, self.config[project_name])
            for project_name in self.config.sections()]

        for template in self.required_templates:
            self._render_raw_template(template)

        self._put_out_jobconfig_list(project_configs)

        self._render_raw_template('composition.groovy')

        return self.output.getvalue()

    def _render_raw_template(self, filename):
        path = pkg_resources.resource_filename(
            'gocept.jenkinsdsl', 'templates/{}'.format(filename))
        with open(path, 'r') as r_f:
            self.output.write(r_f.read())

    def _require_component(self, component):
        component_groovy = '{}.groovy'.format(component)
        if component_groovy not in self.required_templates:
            self.required_templates.append(component_groovy)

    def _require_builder(self, builder):
        if builder:
            self._require_component('builder.abstract')
            self._require_component('builder.{}'.format(builder))

    def _render_jobconfig(self, name, project):

        params = OrderedDict((
            ('name', name),
            ('description', project.get('description', '')),
            ('disabled', project.get('disabled', 'false')),
            ('is_public', project.get('is_public', 'false')),
        ))
        if 'vcs' in project:
            self._require_component(project['vcs'])
            vcs = project['vcs']
            params['vcs'] = self._get_groovy_object_from_name(
                vcs, project, vcs.upper(), name=name)
        if 'builder' in project:
            self._require_builder(project.get('builder'))
            builder = project['builder']
            params['builder'] = self._get_groovy_object_from_name(
                builder, project, self.builder_class_map[builder])
        if 'redmine_website_name' in project:
            self._require_component('redmine')
            params['redmine'] = self._get_groovy_object_from_name(
                'redmine', project, 'Redmine')
        if 'notification_credential_id' in project:
            self._require_component('notification')
            params['notification'] = self._get_groovy_object_from_name(
                'notification', project, 'Notification')
        return self._instantiate_groovy_object('JobConfig', params)

    def _put_out_jobconfig_list(self, configs):
        self.output.write("\\nconfigs = [{}]\\n".format(',\\n'.join(configs)))

    def _render_groovy_params(self, params):
        return ', '.join(["{}: {!r}".format(
                          key, self._escape_newlines(value.strip()))
                          for key, value in params.items()])

    def _instantiate_groovy_object(self, class_, params):
        return GroovyExpression(
            'new {}({})'.format(class_, self._render_groovy_params(params)))

    def _get_groovy_object_from_name(
            self, prefix, project, class_, **defaults):
        prefix = '{}_'.format(prefix)
        params = OrderedDict(defaults)
        params.update((key.replace(prefix, '', 1), GroovyString(value))
                      for key, value in project.items()
                      if key.startswith(prefix))
        return self._instantiate_groovy_object(class_, params)

    def _escape_newlines(self, string):
        return string.replace('\n', '\\n')

    def _escape_dollar(self, string):
        return string.replace('$', r'\$')


def main():
    args = parser.parse_args()
    h = Handler(args.config)
    result = h()
    sys.stdout.write(codecs.decode(result, 'unicode_escape'))


if __name__ == "__main__":
    main()
