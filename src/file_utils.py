import os


def get_files_with_extension(dir_path, ext):
    """
    Get a list of files in a directory (including subdirectories) matching a file extension.
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(ext):
                files.append(os.path.join(dirpath, filename))
    return files
