__author__ = 'tinglev@kth.se'

def args_to_commands(args):
    split_commands = args.split(' ')
    parsed_cmds = []
    current_cmd = ''
    quoted_cmd = False
    for cmd in split_commands:
        if cmd.startswith('"'):
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
