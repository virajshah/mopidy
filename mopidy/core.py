import logging
import optparse
import sys

from pykka.actor import ThreadingActor

from mopidy import get_version, settings, OptionalDependencyError
from mopidy.utils import get_class
from mopidy.utils.log import setup_logging
from mopidy.utils.path import get_or_create_folder, get_or_create_file
from mopidy.utils.process import GObjectEventThread
from mopidy.utils.settings import list_settings_optparse_callback

logger = logging.getLogger('mopidy.core')

def main():
    options = parse_options()
    setup_logging(options.verbosity_level, options.save_debug_log)
    setup_settings()
    setup_gobject_loop()
    setup_output()
    setup_mixer()
    setup_backend()
    setup_frontends()

def parse_options():
    parser = optparse.OptionParser(version='Mopidy %s' % get_version())
    parser.add_option('-q', '--quiet',
        action='store_const', const=0, dest='verbosity_level',
        help='less output (warning level)')
    parser.add_option('-v', '--verbose',
        action='store_const', const=2, dest='verbosity_level',
        help='more output (debug level)')
    parser.add_option('--save-debug-log',
        action='store_true', dest='save_debug_log',
        help='save debug log to "./mopidy.log"')
    parser.add_option('--list-settings',
        action='callback', callback=list_settings_optparse_callback,
        help='list current settings')
    return parser.parse_args()[0]

def setup_settings():
    get_or_create_folder('~/.mopidy/')
    get_or_create_file('~/.mopidy/settings.py')
    settings.validate()

def setup_gobject_loop():
    gobject_loop = GObjectEventThread()
    gobject_loop.start()
    return gobject_loop

def setup_output():
    return get_class(settings.OUTPUT).start().proxy()

def setup_mixer():
    return get_class(settings.MIXER).start().proxy()

def setup_backend():
    return get_class(settings.BACKENDS[0]).start().proxy()

def setup_frontends():
    frontends = []
    for frontend_class_name in settings.FRONTENDS:
        try:
            frontend = get_class(frontend_class_name).start().proxy()
            frontends.append(frontend)
        except OptionalDependencyError as e:
            logger.info(u'Disabled: %s (%s)', frontend_class_name, e)
    return frontends
