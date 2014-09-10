from __future__ import unicode_literals, division, absolute_import
import logging

from flexget import plugin
from flexget.event import event

log = logging.getLogger('parsing')
PARSER_TYPES = ['movie', 'series']


class PluginParsing(object):
    """
    Provides parsing framework
    """

    def __init__(self):
        self.parsers = {}
        self.default_parser = {}
        for parser_type in PARSER_TYPES:
            self.parsers[parser_type] = {}
            for p in plugin.get_plugins(group=parser_type + '_parser'):
                self.parsers[parser_type][p.name.replace('parser_', '')] = p.instance
            # Select default parsers based on priority
            func_name = 'parse_' + parser_type
            self.default_parser[parser_type] = max(self.parsers[parser_type].values(), key=lambda plugin: getattr(getattr(plugin, func_name), 'priority', 0))
        self.parser = self.default_parser

    @property
    def schema(self):
        s = {
            'type': 'object',
            'properties': dict((parser_type, {'type': 'string', 'enum': self.parsers[parser_type]})
                               for parser_type in self.parsers),
            'additionalProperties': False
        }
        return s

    def on_task_start(self, task, config):
        if not config:
            return
        self.parser = self.default_parser.copy()
        for parser_type, parser_name in config.iteritems():
            self.parser[parser_type] = plugin.get_plugin(name='parser_'+parser_name).instance

    def on_task_end(self, task, config):
        self.parser = self.default_parser

    def __getattr__(self, item):
        if not item.startswith('parse_'):
            raise AttributeError(item)
        parser_type = item.replace('parse_', '')
        if parser_type not in self.parser:
            raise AttributeError(item)
        return getattr(self.parser[parser_type], item)


@event('plugin.register')
def register_plugin():
    plugin.register(PluginParsing, 'parsing', api_ver=2)
