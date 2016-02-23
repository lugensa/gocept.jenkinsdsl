import argparse
import pkg_resources
import sys
import codecs
from io import StringIO
from configparser import ConfigParser
from collections import OrderedDict

parser = argparse.ArgumentParser(
    description='Generate DSL to generate Jenkins jobs.')
parser.add_argument('config', type=argparse.FileType('r'), help='Config file.')


class GroovyExpression(str):
    """Is a rendered groovy expression."""

    def __repr__(self):
        return self.__str__()

    def strip(self):
        return self.__class__(super().strip())

    def replace(self, *args, **kw):
        return self.__class__(super().replace(*args, **kw))


class Handler(object):

    builder_class_map = {
        'pytest': 'PytestBuilder',
        'custom': 'CustomBuilder',
    }

    def __init__(self, config_file):
        self.config = ConfigParser()
        self.config.read_file(config_file)
        self.output = StringIO()
        self.required_templates = [
            'header.groovy',
            'interfaces.groovy',
            'builder.abstract.groovy',
            'jobconfig.groovy',
        ]

    def __call__(self):
        project_configs = []
        for project_name in self.config.sections():
            project = self.config[project_name]
            if 'vcs' in project:
                self._require_component(project['vcs'])
            self._require_builder(project.get('builder'))
            if 'redmine_website_name' in project:
                self._require_component('redmine')
            project_configs.append(
                self._render_jobconfig(project_name, project))

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
        self._require_component('builder.abstract')
        self._require_component('builder.{}'.format(builder))

    def _render_jobconfig(self, name, project):

        params = OrderedDict((('name', name),))
        if 'vcs' in project:
            vcs = project['vcs']
            params['vcs'] = self._get_groovy_object_from_name(
                vcs, project, vcs.upper(), name=name)
        if 'builder' in project:
            builder = project['builder']
            params['builder'] = self._get_groovy_object_from_name(
                builder, project, self.builder_class_map[builder])
        if 'redmine_website_name' in project:
            params['redmine'] = self._get_groovy_object_from_name(
                'redmine', project, 'Redmine')
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
        params.update((key.replace(prefix, '', 1), value)
                      for key, value in project.items()
                      if key.startswith(prefix))
        return self._instantiate_groovy_object(class_, params)

    def _escape_newlines(self, string):
        return string.replace('\n', '\\n')


def main():
    args = parser.parse_args()
    h = Handler(args.config)
    result = h()
    sys.stdout.write(codecs.decode(result, 'unicode_escape'))


if __name__ == "__main__":
    main()
