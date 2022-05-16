INSTALLATION:
Mukkava was written primarily for Python 3.9, it requires a Venv or interpriter with access to the following:
    pynacl
    numpy
    pyflac
    sounddevice
    sounddfile

in addition, PortAudio and libsndfile2  must be installed on the system running. Mukkava has primarily been tested on Windows 10, Debian and ubuntu linux, but shouldn't have
any issues running on an evironment that can meet these requirements. if in doubt, the virtual machine in the git repository can be used for testing as it is fully set up to run.

USAGE:
agree upon a symetric key with a peer, and a port to use.
simply run main.py, it will prompt you for any further information required
decide whether you want to wait for inbound connections (enter no to inital peer) or connect directly (yes to inital peer)