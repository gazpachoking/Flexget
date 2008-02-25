import logging

log = logging.getLogger("isohunt")

class ResolveIsoHunt:
    """IsoHunt resolver."""

    def register(self, manager, parser):
        manager.register_resolver(instance=self, name='isohunt')

    def resolvable(self, feed, entry):
        url = entry['url']
        return url.startswith('http://isohunt.com') and url.find('download') == -1
        
    def resolve(self, feed, entry):
        entry['url'] = entry['url'].replace('torrent_details', 'download')
        return True

if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    import test_tools
    test_tools.test_resolver(ResolveIsoHunt())
