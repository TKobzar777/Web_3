from threading import Thread, Event
import logging
import sys
from pathlib import Path
import shutil

CATEGORIES = {"images": ['.JPEG', '.PNG', '.JPG', '.SVG'],
              "video": ['.AVI', '.MP4', '.MOV', '.MKV'],
              "documents": ['.DOC', '.DOCX', '.TXT', '.PDF', '.XLSX', '.PPTX'],
              "audio": ['.MP3', '.OGG', '.WAV', '.AMR'],
              "archives": ['.ZIP', '.GZ', '.TAR']}

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

global list_category
list_category = []

TRANS = {}
for c, l in zip(tuple(CYRILLIC_SYMBOLS), TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def translate(name):
    global TRANS
    return name.translate(TRANS)


def normalize(name_file: str):
    new_name = ""
    name_file = translate(name_file)
    # print(name_file)

    for lit in name_file:
        if ord(lit) == 46 or 48 <= ord(lit) <= 57 or 65 <= ord(lit) <= 90 or 97 <= ord(lit) <= 122:
            new_name = new_name + lit
        else:
            new_name = new_name + "_"
    return new_name


def unp_archives(arch: Path, path: Path) -> None:
    name_ar = arch.stem
    ar_dir_new = path.joinpath(name_ar)
    shutil.unpack_archive(arch, ar_dir_new)


def move_file(file: Path, dir: Path) -> None:
    logging.debug(f'{file} in processed')
    category = get_categories(file)
    target_dir = dir.joinpath(category)

    if not target_dir.exists():
        target_dir.mkdir()
        list_category.append(target_dir)

    file.replace(target_dir.joinpath(normalize(file.name)))


def get_categories(file: Path) -> str:
    suf_f = file.suffix.upper()
    for cat, list_suf in CATEGORIES.items():
        # print(list_suf)
        if suf_f in list_suf:
            return cat
    return "Other"


def rm_empty_dir(event: Event, path: Path) -> None:
    logging.debug('Worker-1 ready to work')
    event.wait()
    logging.debug('The worker can do the work')

    fl = True
    while fl:
        fl = False
        for item in path.glob("**/*"):
            if item.is_dir():
                if item in list_category:
                    continue
                else:
                    if not list(item.iterdir()):
                        item.rmdir()
                        fl = True
                        continue


def unpack_archive(event: Event, path: Path) -> None:
    logging.debug('Worker-2 ready to work')
    event.wait()
    logging.debug('The worker can do the work')
    dir_ar = path.joinpath("archives")
    if dir_ar.exists():
        for ar in dir_ar.iterdir():
            unp_archives(ar, dir_ar)


def check_arg() -> Path | None:
    try:
        path = Path(sys.argv[1])
    except IndexError:
        return None
    # path= Path("C:\\hw_folder")
    if not path.exists:
        return None
    return path


def sort_folder(event: Event, path: Path) -> None:
    logging.debug('Master doing some work')
    threads = []
    for item in path.glob("**/*"):
        if item.is_file():
            thread = Thread(target=move_file, args=(item, path))
            thread.start()
            threads.append(thread)
    [el.join() for el in threads]
    logging.debug('End moving file')
    logging.debug('Informing that workers can do the work')
    event.set()


if __name__ == "__main__":
    path = check_arg()
    if not path:
        print("No argument entered or folder is empty!")
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    logging.debug('Start')
    event = Event()
    master = Thread(name='master', target=sort_folder, args=(event, path))

    worker_one = Thread(name='worker_one', target=unpack_archive, args=(event, path))
    worker_two = Thread(name='worker_two', target=rm_empty_dir, args=(event, path))
    worker_one.start()
    worker_two.start()
    master.start()
    logging.debug('End program')
