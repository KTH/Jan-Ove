__author__ = 'tinglev'

import coloredlogs
import logging
import os

log = logging.getLogger(__name__)


def init_logging():
    field_style_override = coloredlogs.DEFAULT_FIELD_STYLES
    level_style_override = coloredlogs.DEFAULT_LEVEL_STYLES
    logging_level = 'INFO'
    if os.environ.get('DEBUG'):
        logging_level = 'DEBUG'
    field_style_override['levelname'] = {"color": "magenta", "bold": True}
    level_style_override['debug'] = {'color': 'blue'}
    coloredlogs.install(level=logging_level,
                        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
                        level_styles=level_style_override,
                        field_styles=field_style_override)
    log.info('Log level set to "%s"', logging_level)
