"""
This module must stay side-effect free and must not import any other BAAH module. Entry points import it before everything else, and importing
something like modules.utils would construct the MyConfig singleton, which is the very thing that needs a correct working directory.

The codebase uses cwd-relative paths such as "./DATA/xxx" throughout, so the whole program assumes cwd is the app root. Launching from the Windows
search bar or from Task Scheduler gives the process a cwd of C:\\WINDOWS\\system32, which breaks that assumption and crashes BAAH during import.
"""
import os
import sys


def get_app_root() -> str:
    """
    Return the app root, the folder that holds BAAH_CONFIGS/, DATA/ and tools/.

    Returns:
        Absolute path of the app root.
    """
    # Once packaged, sys.executable points at BAAH.exe, which is correct for both onedir and onefile builds.
    # Do not use sys._MEIPASS: in onefile mode it is a temp unpack folder deleted on exit, and the user data does not live there.
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.realpath(sys.executable))
    # Running from source, sys.executable is python.exe, so go two levels up from __file__ instead.
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def chdir_to_app_root() -> str:
    """
    Switch the process working directory to the app root. The target does not depend on the current cwd, so calling this repeatedly is idempotent.

    Returns:
        Absolute path of the app root.
    """
    root = get_app_root()
    try:
        os.chdir(root)
    except OSError as e:
        # Do not raise here, let the real failure further along carry a more meaningful stack.
        print(f"[BAAH] 无法切换工作目录到 {root}: {e}")
        print(f"[BAAH] Failed to chdir to app root {root}: {e}")
    return root
