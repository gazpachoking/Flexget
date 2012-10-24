import npyscreen
import curses
from flexget.plugin import register_parser_option, DependencyError
from flexget.event import event
from flexget.manager import Session

try:
    from flexget.plugins.filter.series import SeriesDatabase, Series, Episode, Release, forget_series, forget_series_episode
except ImportError:
    raise DependencyError(issued_by='cli_series', missing='series', message='Series commandline interface not loaded')

class SeriesTreeLineAnnotated(npyscreen.TreeLineAnnotated):
    def getAnnotationAndColor(self):
        if not self.value:
            return '', 'CONTROL'
        return self.value['ann'].rjust(6), self.value['ann_color']

    def display_value(self, vl):
        if not vl:
            return
        return vl['text']

class SeriesTree(npyscreen.MultiLineTreeNewAction):
    _contained_widgets = SeriesTreeLineAnnotated

    def display_value(self, vl):
        content = vl.getContent()
        text = ''
        ann = ''
        ann_color = 'CONTROL'
        if isinstance(content, Series):
            text = content.name
            ann = '------'
            if not vl.expanded:
                text += ' - %s episode' % len(content.episodes)
                if len(content.episodes) > 1:
                    text += 's'
        elif isinstance(content, Episode):
            text = content.identifier
            text += ' (' + content.identified_by + ')'
            if not vl.expanded:
                text += ' - %s release' % len(content.releases)
                if len(content.releases) > 1:
                    text += 's'
        elif isinstance(content, Release):
            if content.downloaded:
                ann = '*'
            text = content.title + ' [' + str(content.quality) + ']'
        return {'text': text, 'ann': ann, 'ann_color': ann_color}

class SeriesForm(npyscreen.FormBaseNewExpanded):
    def create(self):
        self.series_view = self.add(SeriesTree, values=create_tree_data())

    #  No clue what I'm doing here, but this seems to exit when ESC is pushed.
    def set_up_exit_condition_handlers(self):
        self.how_exited_handers = {
            True: self.exit_app
        }

    def exit_app(self):
        self.editing = False

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