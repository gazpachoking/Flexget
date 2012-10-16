import npyscreen
from flexget.plugin import register_parser_option, DependencyError
from flexget.event import event
from flexget.manager import Session

try:
    from flexget.plugins.filter.series import SeriesDatabase, Series, Episode, Release, forget_series, forget_series_episode
except ImportError:
    raise DependencyError(issued_by='cli_series', missing='series', message='Series commandline interface not loaded')

class SeriesTree(npyscreen.MultiLineTreeNew):
    def display_value(self, vl):
        content = vl.content
        if isinstance(content, Series):
            return content.name
        elif isinstance(content, Episode):
            return content.identifier
        elif isinstance(content, Release):
            return content.title

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
        tree_series = tree_root.newChild(content=series)
        for episode in session.query(Episode).join(Series).filter(Series.id == series.id):
            tree_ep = tree_series.newChild(content=episode)
            for release in session.query(Release).join(Episode).filter(Episode.id == episode.id):
                tree_ep.newChild(content=release)
    return tree_root


@event('manager.startup')
def run(manager):
    if manager.options.series_interactive:
        manager.disable_tasks()
        npyscreen.wrapper_basic(myFunction)

register_parser_option('--series-interactive', action='store_true')