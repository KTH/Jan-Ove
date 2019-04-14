__author__ = 'tinglev@kth.se'

import logging

def args_to_commands(args):
    log = logging.getLogger(__name__)
    # Fix slacks curly quotation marks
    args = args.replace('“', '"').replace('”', '"')
    log.debug('Converting "%s" to command list', args)
    split_commands = args.split(' ')
    parsed_cmds = []
    current_cmd = ''
    quoted_cmd = False
    for cmd in split_commands:
        if cmd.startswith('"') and cmd.endswith('"'):
            parsed_cmds.append(cmd.replace('"', ''))
        elif cmd.startswith('"'):
            current_cmd = cmd.replace('"', '')
            quoted_cmd = True
        elif cmd.endswith('"'):
            current_cmd += ' ' + cmd.replace('"', '')
            parsed_cmds.append(current_cmd)
            quoted_cmd = False
        elif quoted_cmd:
            current_cmd += ' ' + cmd
        else:
            parsed_cmds.append(cmd)
    return parsed_cmds
