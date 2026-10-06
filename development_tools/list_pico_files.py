import os


def walk(path):

    for name in os.listdir(path):

        if path == "/":
            full_path = "/" + name
        else:
            full_path = path + "/" + name

        try:
            # If this succeeds, it is a directory.

            os.listdir(full_path)

            walk(full_path)

        except OSError:
            # Otherwise, it is a file.

            print(full_path)


walk("/")