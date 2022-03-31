"""
This module is responsible for the following tasks:
    Audio recording and playback, Opus encoding and decoding.

FOR DISSERTATION
https://github.com/TaylorSMarks/playsound - considered, but not used due to a lack of ability recording
https://python-sounddevice.readthedocs.io/en/0.4.4/usage.html# and https://pypi.org/project/PyAudio/ considered, but dropped due to not having simple mechanisms to allow for the playing of a file that is being updated by a stream
https://github.com/orion-labs/opuslib - considered, but dropped due to lack of support and updates likely will not work with later libopus versions.
https://github.com/TeamPyOgg/PyOgg - not feature complete, doesn't have an encoder or decoder (look at issues)
https://github.com/Zuzu-Typ/PyOpenAL - Tested, but decided not to use as it doesn't have support for openAL's recording functions, Streaming audio seems funky too.
"""
import soundfile as sf
import sounddevice as sd
import numpy; assert numpy  # numpy is utilised by sounddevice, but sounddevice doesn't show this to the interpreter so we have to assert it to stop pep warnings
import pyflac
import queue


sd.default.channels = 2
sd.default.samplerate = 48000
sd.default.blocksize = 0
sd.default.latency = 'low' # sd (or port audio rather) defaults to 'high' for this typically, if your getting wierd behaviour try setting it high
sd.default.dtype = 'int16' # has to be int16, int32 or float32 / 64 are too high a bitdepth and make pyflacc unhappy

def audio_setup(operation):  #Responsible for inital audio device setup
    if operation == "list":
        print(f"available devices to use are bellow: \n{sd.query_devices()} \nDefault devices (input, output) are set to: {sd.default.device}")

    if operation == "set":
        sd.default.device = int(input("Desired input device ID: ")), int(input("Desired output device ID: "))
        print(f"Default devices were set to: {sd.default.device}")

    if operation =="test":
        input("Hit enter to test recording via input device ")
        test = sd.rec(3 * sd.default.samplerate)
        print("RECORDING")
        sd.wait()
        input("Hit enter to test playback via output device ")
        sd.play(test)
        print("PLAYING")
        sd.wait()



class Audio_input: #Sets up a sound device input stream, a flacc encoder, and a data buffer for recording audio from a microphone
    def __init__(self):
        self.instream = sd.InputStream(callback=self.instream_callback)
        self.flacc_encoder = pyflac.StreamEncoder(write_callback=self.encoder_callback, sample_rate=sd.default.samplerate, compression_level=5)
        self.data_buffer = queue.SimpleQueue()

    def instream_callback(self, indata, frames, sd_time, status):   #called by instream once it has data, calls the encoder to process raw input data it recieves
        self.flacc_encoder.process(indata)

    def encoder_callback(self, buffer, num_bytes, num_samples, current_frame):  #called by flacc_encoder once it has encoded data, stores encoded data in data_buffer
        self.data_buffer.put(buffer)


class Audio_output:
    def __init__(self):
        self.data_buffer = queue.SimpleQueue()
        self.outstream = sd.OutputStream(callback=self.outstream_callback)
        self.flacc_decoder = pyflac.StreamDecoder(write_callback=self.decoder_callback, sample_rate=sd.default.samplerate)

    def process(self):
        while not self.data_buffer.empty():
            self.flacc_decoder.process(self.queue.get())

    def decoder_callback(self, data, sample_rate, num_channels, num_samples):
        self.output.write(data)

audio = Audio_output()
audio.outstream.start()

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