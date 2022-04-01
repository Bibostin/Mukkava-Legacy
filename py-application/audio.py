"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    Flac encoding and decoding
    Audio recording for outbound packets
    Mixing inbound packets into a single source for audio playback
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
    Latency = blocksize (buffer size) / sample rate nominally, this programs latency (excluding network travel time) with the current default values is 5.3ms, not bad.
    if you are not explitly setting samplerate and blocksize as I am doing above to make sd and pyflac play nice together however, you could set these values to 0 which
    tells sd to change this equation dynamically. Alternatively  #sd.default.latency = 'seconds' can be used which tells sd how many seconds sd should aim for between
    stream data being produced, this can also be set to "low" or high" which use your input / output devices maximum or minimum respectively.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
     audio_in = Audio_input()
     audio_out = Audio_output()
     audio_in.instream.start()
     audio_out.outstream.start()
     while True:
         audio_out.data_decode_buffer.put(audio_in.data_buffer.get())
         audio_out.process()
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
https://github.com/TaylorSMarks/playsound - considered, but not used due to a lack of ability recording.
https://python-sounddevice.readthedocs.io/en/0.4.4/usage.html# and https://pypi.org/project/PyAudio/ considered, but dropped due to not having simple mechanisms to allow for the playing of a file that is being updated by a stream
https://github.com/orion-labs/opuslib - considered, but dropped due to lack of support and updates likely will not work with later libopus versions.
https://github.com/TeamPyOgg/PyOgg - not feature complete, doesn't have an encoder or decoder (look at issues, while a py file for both is present in their github ver, neither are in __py_init__ and can't be used as a method reliably)
https://github.com/Zuzu-Typ/PyOpenAL - Tested, but decided not to use as it doesn't have support for openAL's recording functions, Streaming audio seems funky too.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

import soundfile as sf
import sounddevice as sd  # Sound device, portaudio wrapper for recording and playback of audio
import numpy; assert numpy  # numpy is utilised by sounddevice, but sounddevice doesn't show this to the interpreter so we have to assert it to stop pep warnings
import pyflac  #Python implementation of the flac standard, used for encoding and decoding
import queue  #used for buffering input and output sound data for transmission / playback

sd.default.channels = 2 # Default number of channels sd will attempt to use for input and output devices (I use 2 for Stereo audio.)
sd.default.dtype = 'int16' # bit depth for a singular sample frame. pyFLAC currently only supports 16-bit audio, sd supports greater values.
sd.default.samplerate = 48000  # Sampling rate (how many samples frames to take per second) for audio data. higher value = greater audio depth, but larger performance overhead.
sd.default.blocksize = 256 #  lower value = less latency, but more performance overhead


def audio_device_setup():  #Responsible for inital audio device listing, setup and testing    if operation == "list":
        print(f"available devices to use are bellow: \n{sd.query_devices()} \nDefault devices (input, output) are set to: {sd.default.device}")
        sd.default.device = int(input("Desired input device ID: ")), int(input("Desired output device ID: "))
        print(f"Default devices were set to: {sd.default.device}")
        input("Hit enter to test recording via input device ")
        test = sd.rec(3 * sd.default.samplerate)
        print("RECORDING")
        sd.wait()
        input("Hit enter to test playback via output device ")
        sd.play(test)
        print("PLAYING")
        sd.wait()


class Audio_input: #Sets up a sound device input stream, a flacc encoder, takes pynum array input audio, encodes it, then puts it in a queue for serialisation.
    def __init__(self):
        self.instream = sd.InputStream(callback=self.instream_callback)
        self.flacc_encoder = pyflac.StreamEncoder(write_callback=self.encoder_callback, blocksize=sd.default.blocksize, sample_rate=sd.default.samplerate, compression_level=5)
        self.data_buffer = queue.SimpleQueue()

    def instream_callback(self, indata, frames, sd_time, status):   #called by instream once it has data, calls the encoder to process raw input data it recieves
        self.flacc_encoder.process(indata)

    def encoder_callback(self, buffer, num_bytes, num_samples, current_frame):  #called by flacc_encoder once it has encoded data, stores encoded data in data_buffer
        self.data_buffer.put(buffer)


class Audio_output:
    def __init__(self):
        self.data_decode_buffer = queue.SimpleQueue()
        self.data_playback_buffer = queue.SimpleQueue()
        self.outstream = sd.OutputStream(callback=self.outstream_callback)
        self.flacc_decoder = pyflac.StreamDecoder(write_callback=self.decoder_callback)

    def process(self):
        if not self.data_decode_buffer.empty():
            self.flacc_decoder.process(self.data_decode_buffer.get_nowait())


    def decoder_callback(self, buffer, sample_rate, num_channels, num_samples):
        self.data_playback_buffer.put(buffer)

    def outstream_callback(self, outdata, frames, sd_time, status):
        if not self.data_playback_buffer.empty():
            outdata[:] = self.data_playback_buffer.get_nowait()


#Queue(maxsize=args.buffersize)
# data_1, fs_1 = sf.read('sound_file_1.wav', dtype='float32')
# data_2, fs_2 = sf.read('sound_file_2.wav', dtype='float32')
#
# if len(data_1) > len(data_2):
#     data = data_1 + np.pad(data_2, (0, len(data_1) - len(data_2)))
# else:
#     data = np.pad(data_1, (0, len(data_2) - len(data_1))) + data_2
#
# # determine fs from a combination of fs_1 and fs_2 of your choosing, like
# fs = min(fs_1, fs_2)
#
# sd.play(data, fs)