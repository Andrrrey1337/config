import os
import socket
import shlex
import sys


def get_prompt():
    username = os.getlogin()
    hostname = socket.gethostname()
    current_dir = "~"  # заглушка
    return f"{username}@{hostname}:{current_dir}$ "


def parser(line):
    tokens = shlex.split(line)
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]


def cmd_ls(args):
    print(f"ls {' '.join(args)}")


def cmd_cd(args):
    print(f"cd {' '.join(args)}")


def cmd_exit():
    print("Выход")
    sys.exit(0)


while True:
    try:
        line = input(get_prompt()).strip()
        cmd, args = parser(line)

        if cmd == "ls":
            cmd_ls(args)
        elif cmd == "cd":
            cmd_cd(args)
        elif cmd == "exit":
            cmd_exit()
        else:
            print(f"Неизвестная команда: {cmd}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\n(Для выхода введите 'exit')")
    except EOFError:
        print("\nВыход через EOF")
        break
    except ValueError as e:
        print(f"Ошибка ввода: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
