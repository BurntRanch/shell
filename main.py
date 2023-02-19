import os, subprocess
import readline

# USER or USERNAME (prefer USER)
username = os.environ.get('USER', os.environ.get('USERNAME', None))
homeDir = os.environ.get('HOME')
inputPrompt = username + ' at {{DIR}} >'
inputPrompt += '# ' if os.geteuid() == 0 else '$ '

cache = {}

def formatInputPrompt():
    return inputPrompt.replace('{{DIR}}', os.getcwd().replace(homeDir, '~'))

def shellExit(args):
    exit(0)

def changeDirectory(args):
    if len(args) == 0:
        os.chdir(homeDir)
    try:
        os.chdir(args[0].replace('~', homeDir))
    except FileNotFoundError:
        print('Directory does not exist!')
    except NotADirectoryError:
        print('Not a directory!')

def shellBreakpoint(args):
    breakpoint()

def startExpression(args):
    if len(args) < 4:
        print('Invalid syntax! Syntax: ( x y z )')
        return
    operandOne = int(args[0]) if args[0].isnumeric() else None
    operation = args[1]
    operandTwo = int(args[2]) if args[2].isnumeric() else None
    if operandOne is None or operandTwo is None:
        print('The two operands have to be numerical.')
    match operation:
        case '>':
            print(operandOne > operandTwo)
        case '<':
            print(operandOne < operandTwo)
        case '>=':
            print(operandOne >= operandTwo)
        case '<=':
            print(operandOne <= operandTwo)

while True:
    # Some commands don't perform well due to them running in a *subprocess*, so we have to replace them with python implementations.
    commands = {'exit': shellExit, 'cd': changeDirectory, 'breakpoint': shellBreakpoint, '(': startExpression}

    cmd = input(formatInputPrompt()).split(' ')

    if not (' '.join(cmd)).isspace() and (' '.join(cmd)) != '':
        if cmd[0] in commands:
            commands[cmd[0]](cmd[1:])

        # We don't want to keep looking up spaces or '' in the shell
        else:
            # We also don't want to keep looking up commands that we already looked up
            if cmd[0] in cache and os.path.isfile(cache[cmd[0]]):
                try:
                    subprocess.run([cache[cmd[0]], *cmd[1:]])
                    continue
                # Maybe it's just the cache..
                except OSError:
                    pass
            found = False
            for path in os.environ.get('PATH').split(':'):
                file = os.path.join(path, cmd[0])
                if os.path.exists(file):
                    try:
                        subprocess.run([file, *cmd[1:]])
                        cache[cmd[0]] = file
                        found = True
                    except OSError as e:
                        print(f'[OS ERROR!] {e.errno}:{e.strerror}')
                    finally:
                        break
            if not found:
                if os.path.isfile(cmd[0]):
                    try:
                        subprocess.run([os.path.abspath(cmd[0]), *cmd[1:]])
                        cache[cmd[0]] = cmd[0]
                    except OSError as e:
                        print(f'[OS ERROR!] {e.errno}:{e.strerror}')
                    finally:
                        continue
                print('Command not found!')
