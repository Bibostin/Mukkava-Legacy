import sounddevice as sd  # Sound device, portaudio wrapper for recording and playback of audio
import numpy; assert numpy  # numpy is utilised by sounddevice, but sounddevice doesn't show this to the interpreter so we have to assert it to stop pep warnings
import pyflac  #Python implementation of the flac standard, used for encoding and decoding
import queue  #used for buffering input and output sound data for transmission / playback

#sd default value setup: these are used in many of the bellow functions as default values, setting here allows for quick changes to the entire program.
sd.default.channels = 2 # Default number of channels sd will attempt to use for input and output devices (Stereo)
sd.default.samplerate = 48000  #Sampling rate for audio data (48Khz is on the edge of audio transparency for human hearing)
sd.default.blocksize = 1024 # How large each section 0 is a special assignment that makes sounddevice attempt to match latency.
sd.default.latency = 'low' # sd (or port audio rather) defaults to 'high' for this typically, if your getting wierd behaviour try setting it high
sd.default.dtype = 'int16' # has to be int16, int32 or float32 / 64 are too high a bitdepth  (pyFLAC currently only supports 16-bit audio.)

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



class Audio_input: #Sets up a sound device input stream, a flacc encoder, and a data buffer for recording audio from a microphone
    def __init__(self):
        self.instream = sd.InputStream(callback=self.instream_callback)
        self.flacc_encoder = pyflac.StreamEncoder(write_callback=self.encoder_callback, sample_rate=sd.default.samplerate, compression_level=5)
        self.data_buffer = queue.SimpleQueue()

    def instream_callback(self, indata, frames, sd_time, status):   #called by instream once it has data, calls the encoder to process raw input data it recieves
        self.data_buffer.put(indata)


    def encoder_callback(self, buffer, num_bytes, num_samples, current_frame):  #called by flacc_encoder once it has encoded data, stores encoded data in data_buffer
        self.flacc_encoder.process(buffer)

def test_callback(indata, frames, sd_time, status):
    indata[:] = audio_in.data_buffer.get()

audio_device_setup()
audio_in = Audio_input()

outstream = sd.OutputStream(callback=test_callback)


audio_in.instream.start()
outstream.start()

while True:
    print ("working")