"""
#DESIGN NOTES
This module is responsible for the following major tasks:
    Detecting microphone activation, and buffering user speach for serialization (asynchronously)
    Playback of received co-user audio streams (asynchronously)
    Opus encoding / decoding input and received signals
    Audio settings (microphone sensitivity, user volume, etc.)

FOR DISSERTATION
https://github.com/TaylorSMarks/playsound - considered, but not used due to a lack of ability recording
https://python-sounddevice.readthedocs.io/en/0.4.4/usage.html# and https://pypi.org/project/PyAudio/ considered, but dropped due to not having simple mechanisms to allow for the playing of a file that is being updated by a stream
https://github.com/orion-labs/opuslib - considered, but dropped due to lack of support and updates, likely wont work with later libopus verisons.
https://github.com/Zuzu-Typ/PyOpenAL - Tested, but decided not to use as it doesn't have support for openAL's recording functions, Streaming audio seems funky too.
"""

