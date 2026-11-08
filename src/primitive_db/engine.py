import prompt


def _print_help():
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")
    _print_help()
    while True:
        command = prompt.string("Введите команду: ")
        if command == "help":
            print()
            _print_help()
        elif command == "exit":
            break
