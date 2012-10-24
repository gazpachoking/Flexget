import npyscreen
from flexget.plugin import register_parser_option, DependencyError
from flexget.event import event
from flexget.manager import Session

try:
    from flexget.plugins.filter.series import SeriesDatabase, Series, Episode, Release, forget_series, forget_series_episode
except ImportError:
    raise DependencyError(issued_by='cli_series', missing='series', message='Series commandline interface not loaded')

class SeriesTreeLineAnnotated(npyscreen.TreeLineAnnotated):
    def getAnnotationAndColor(self):
        annotate = ''
        color = self._annotatecolor
        if hasattr(self.value, 'annotate'):
            annotate = self.value.annotate
        return annotate.center(7), color

    def display_value(self, vl):
        if not vl:
            return
        content = vl.getContent()
        result = ''
        if isinstance(content, Series):
            result = content.name
            if not vl.expanded:
                result += ' - %s episodes' % len(content.episodes)
        elif isinstance(content, Episode):
            result = content.identifier
            if not vl.expanded:
                result += ' - %s releases' % len(content.releases)
        elif isinstance(content, Release):
            if content.downloaded:
                vl.annotate = '*'
            result = content.title
        return result

class SeriesTree(npyscreen.MultiLineTreeNew):
    _contained_widgets = SeriesTreeLineAnnotated
    def display_value(self, vl):
        return vl

class SeriesForm(npyscreen.Form):
    def create(self):
        a = npyscreen.NPSTreeData()
        a.newChild(content='a').newChild('c')
        a.newChild(content='b')
        self.series_view = self.add(SeriesTree, values=create_tree_data())

def myFunction(*args):
    F = SeriesForm(name = "Series View")
    F.edit()

def create_tree_data():
    session = Session()
    tree_root = npyscreen.NPSTreeData()
    for series in session.query(Series):
        tree_series = tree_root.newChild(content=series, expanded=False)
        for episode in series.episodes:
            tree_ep = tree_series.newChild(content=episode, expanded=False)
            for release in episode.releases:
                tree_ep.newChild(content=release)
    return tree_root


@event('manager.startup')
def run(manager):
    if manager.options.series_interactive:
        manager.disable_tasks()
        npyscreen.wrapper_basic(myFunction)

register_parser_option('--series-interactive', action='store_true')