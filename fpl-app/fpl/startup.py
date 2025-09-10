# startup.py
import threading

from fpl.dataloader.load_data import load


def startup():
    load_thread = threading.Thread(target=load)
    load_thread.start()
