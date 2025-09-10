from queue import Queue


def copy_queue(source):
    target = Queue()
    temp = []
    # First copy the source queue to the target
    while not source.empty():
        entry = source.get()
        temp.append(entry)
        target.put(entry)

    for entry in temp:
        source.put(entry)

    return (source, target)