import argparse
import os
import socket
import shlex
import sys
import xml.etree.ElementTree
import base64

vfs_data = {}


def load_vfs(path_xml):
    global vfs_data
    try:
        tree = xml.etree.ElementTree.parse(path_xml)
        root = tree.getroot()

        parse_vfs(root, "")
    except Exception as e:
        print(f"Ошибка загрузки: {e}", file=sys.stderr)
        sys.exit(1)


def parse_vfs(node, path):
    global vfs_data
    for child in node:
        name = child.get("name")
        new_path = path + "/" + name
        if child.tag == "dir":
            vfs_data[new_path] = "dir"
            parse_vfs(child, new_path)
        elif child.tag == "file":
            content = child.text
            try:
                content = base64.b64decode(content).decode("utf-8")
            except Exception:
                content = "Ошибка декодирования"
            vfs_data[new_path] = content


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


def execute_command(cmd, args):
    if cmd == "ls":
        cmd_ls(args)
        return True
    elif cmd == "cd":
        cmd_cd(args)
        return True
    elif cmd == "exit":
        cmd_exit()
        return False
    else:
        print(f"Неизвестная команда: {cmd}", file=sys.stderr)
        return False


def interactive():
    while True:
        try:
            line = input(get_prompt()).strip()
            cmd, args = parser(line)
            execute_command(cmd, args)

        except EOFError:
            print("\nВыход через EOF")
            break
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)


def script(script_path):
    try:
        f = open(script_path, 'r', encoding="utf-8").readlines()
    except Exception as e:
        print(f"Ошибка чтения скрипта {script_path} : {e}", file=sys.stderr)
        sys.exit(1)

    for line in f:
        if not line or line.startswith("#"):
            continue
        line = line.strip()
        print(get_prompt() + line)

        try:
            cmd, args = parser(line)
            if not execute_command(cmd, args):
                sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)


parse = argparse.ArgumentParser()
parse.add_argument("--vfs-path", type=str, help="Путь к расположению VFS")
parse.add_argument("--startup-script", type=str, help="Путь к скрипту")
args = parse.parse_args()

print(f"VFS path: {args.vfs_path if args.vfs_path else 'не задан'}")
print(f"Star script: {args.startup_script if args.startup_script else 'не задан'}")

if args.vfs_path:
    load_vfs(args.vfs_path)

if args.startup_script:
    script(args.startup_script)
else:
    interactive()
