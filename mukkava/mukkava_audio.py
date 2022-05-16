"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    Audio device setup
    Flac encoding and decoding
    Audio recording for outbound packets
    Mixing inbound packets into a single source for audio playback

    Testing files for implementing this module can be found in /testing/first_party_tests/sounddevice_experimentation
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
    Latency = blocksize (buffer size) / sample rate nominally, this programs latency (excluding network travel time / mixing) with the current default values is 5.3ms, not bad.
    if you are not explitly setting samplerate and blocksize as I am doing above to make sd and pyflac play nice together however, you could set these values to 0 which
    tells sd to change this equation dynamically. Alternatively  #sd.default.latency = 'seconds' can be used which tells sd how many seconds sd should aim for between
    stream data being produced, this can also be set to "low" or high" which use your input / output devices maximum or minimum respectively.

    There are two approaches that can be taken when it comes to mixing audio, approach one where each socket creates its own AudioOutput instance, and vies for control of the output
    device (this is simple to implement, but resource intensive) and approach two, where only a single instance of AudioOutput is used and audio is sourced from a multitude of
    buffers, mixed then sent to the playback device (a little more complex, and with the potential for latency issues, but significantly less resource intensive.)

    blocksize had to be increased substantially from 128 to 1248 when introducing mixing because the mixing process with low blocksize (and thus high num of operations) introduced
    processing latency that detracted from audio quality. it had to be increased again to 2000, after implementing mukkava socket as the current networking implementation has a big
    impact on performance, especially with multiple clients.

    The current mixer implementation doesnt care for what specific buffer processed data came from, merely that it is a distinct element that can be mixed. if you wanted to perform
    processing on specific data (eq, compression or volume leveling per user) pyflac would need to be modified so the callback could track this and put the data in a specific processing
    buffer.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
    #Note because sd does not allow for multiple streams to access the same input device we cannot locally test mixing, however if you look at sd_mixing.py the theory is the same,
    #the bellow code merely verifies the audio stack is working as intended.
     audiosetup()
    audio_in = AudioInput()
    audio_out = AudioOutput()

    audio_out_buffer_instance1 = audio_out.add_queue()

    audio_in.instream.start()
    audio_out.outstream.start()

    print("now in audio stream loop, talk to hear latency of audio with encoding, decoding and faux mixing")
    while True:
        audio_out_buffer_instance1.put(audio_in.data_buffer.get())
        audio_out.process_input()

    #You can find the rough expected charecter size of each piece of encoded input device audio data with the following code, useful for determining the required length of theunencrypted headersize.
    #the current setup ranges from 1200 to 2200~ thus a minimum of 3 charecters (or bytes rather) are needed for headersize as 3^8 = 6561 but 2^8 = 256
    audio_in = AudioInput()
    audio_in.instream.start()
    while True:
        encoded_data = audio_in.data_buffer.get()
        print(encoded_data)
        print(len(encoded_data))
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
https://github.com/TaylorSMarks/playsound - considered, but not used due to a lack of ability recording.
https://python-sounddevice.readthedocs.io/en/0.4.4/usage.html# and https://pypi.org/project/PyAudio/ considered, but dropped due to not having simple mechanisms to allow for the playing of a file that is being updated by a stream
https://github.com/orion-labs/opuslib - considered, but dropped due to lack of support and updates likely will not work with later libopus versions.
https://github.com/TeamPyOgg/PyOgg - not feature complete, doesn't have an encoder or decoder (look at issues, while a py file for both is present in their github ver, neither are in __py_init__ and can't be used as a method reliably)
https://github.com/Zuzu-Typ/PyOpenAL - Tested, but decided not to use as it doesn't have support for openAL's recording functions, Streaming audio seems funky too.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import sounddevice as sd  # Sound device, portaudio wrapper for recording and playback of audio
import numpy; assert numpy  # numpy is utilised by sounddevice, but sounddevice doesn't show this to the interpreter so we have to assert it to stop pep warnings
import pyflac  # Python implementation of the flac standard, used for encoding and decoding
import queue  # used for buffering input and output sound data for transmission / playback

sd.default.channels = 2  # Default number of channels sd will attempt to use for input and output devices (I use 2 for Stereo audio.)
sd.default.dtype = 'int16'  # bit depth for a singular sample frame. pyFLAC currently only supports 16-bit audio, sd supports greater values.
sd.default.samplerate = 48000  # Sampling rate (how many samples frames to take per second) for audio data. higher value = greater audio depth, but larger performance overhead.
sd.default.blocksize = 2500  # lower value = less latency, but more performance overhead

def audiosetup():  # Responsible for inital audio device listing, setup and testing    if operation == "list":
    print(f"available devices to use are bellow: \n{sd.query_devices()} \nDefault devices (input, output) are currently set to: {sd.default.device}")
    while True:
        try: sd.default.device = int(input("Desired input device ID: ")), int(input("Desired output device ID: ")); break
        except ValueError: print("supplied device id is a charecter, supply a numeric value")
    print(f"Default devices were set to: {sd.default.device}")
    input("Hit enter to test recording via input device ")
    test = sd.rec(3 * sd.default.samplerate)
    print("RECORDING")
    sd.wait()
    input("Hit enter to test playback via output device ")
    sd.play(test)
    print("PLAYING")
    sd.wait()


class AudioInput:  # Sets up a sound device input stream & flacc encoder. instream generates input audio data, passes it to flac which encodes it, then puts it in a queue for serialisation.
    def __init__(self):
        self.instream = sd.InputStream(callback=self.instream_callback)
        self.flac_encoder = pyflac.StreamEncoder(write_callback=self.encoder_callback, blocksize=sd.default.blocksize, sample_rate=sd.default.samplerate, compression_level=5)
        self.data_buffer = queue.SimpleQueue()

        #Pyflac allways starts a encode stream with some string information pertaining to the encoder, however mukkava_encryption catches this a utf-8 segment it can decode into a string which errors pyflacs decoder as it needs bytes, not strings
        #This may seem unelegant but its simple and the alternative is checking the individual encoding of the first couple of sets data with cchardet to see if they are encoded in 'WINDOWS-1252' which is space costly.
        self.instream.start()
        for loops in range(3): # The offending string are in the first-third sent segments of "audio data", so we need to clear up to there.
            self.data_buffer.get()
        self.instream.stop()

    def instream_callback(self, indata, frames, sd_time, status):   # called by instream once it has data, calls the encoder to process raw input data it recieves
        self.flac_encoder.process(indata)  #this is fine as flac_encoder.process() is not blocking

    def encoder_callback(self, buffer, num_bytes, num_samples, current_frame):  # called by flacc_encoder once it has encoded data, stores encoded data in data_buffer
        self.data_buffer.put(buffer)


class AudioOutput:  # Sets up a sound device output stream & flacc decoder. takes encoded flac stream/s decodes them, mixes them into a single source then puts into a buffer for playback.
    def __init__(self):
        self.data_decode_buffer_array = []  # array of buffers for incoming data from sockets that needs to be decoded
        self.data_mixing_array = []  # array of int16 numpy decoded data to be mixed into a final source for playback
        self.data_playback_buffer = queue.SimpleQueue()  # buffer for processed data that can be played back to client
        self.outstream = sd.OutputStream(callback=self.outstream_callback)  # a sd output playback stream that takes numpy arrays and converts to sound
        self.flac_decoder = pyflac.StreamDecoder(write_callback=self.decoder_callback)  # A pyflac decoder that converts encoded flac files back to numpy arrays

    def add_queue(self):  # function that when called, adds a new queue to the decode and mixing buffer arrays, required to initalise a new socket instances individual buffers.
        self.data_decode_buffer_array.append(queue.SimpleQueue())  #  add a new buffer to the array
        return self.data_decode_buffer_array[-1]  #fetch the last element of our array (Which should be the one we just added)

    def process_input(self):  # function that when called, checks for data in each decode buffer, if present calls the decoder to process the next piece of data
        for buffer_number in range(0, len(self.data_decode_buffer_array)):
            if not self.data_decode_buffer_array[buffer_number].empty():  # if the specific buffer we are accessing is not empty
                self.flac_decoder.process(self.data_decode_buffer_array[buffer_number].get_nowait())  # process the data with our flac decoder
        self.process_input_callback()  #once we have decoded an entire set of buffer audio data we need to mix it.

    def decoder_callback(self, buffer, sample_rate, num_channels, num_samples):  # called by flac_decoder once it has decoded data, appends the data to the mixing array for mixing.
        self.data_mixing_array.append(buffer)

    def process_input_callback(self):
        self.data_playback_buffer.put(sum(self.data_mixing_array))  #Sum all of our numpy arrays (if there are multiple) together to get a mixed source.
        self.data_mixing_array.clear()  # Flush the mixing array for new data.


    def outstream_callback(self, outdata, frames, sd_time, status):  # called by outstream to fetch new audio data autonmously from the above, if data is present in the playback buffer, its fed into the outputstream.
        if not self.data_playback_buffer.empty():
            outdata[:] = self.data_playback_buffer.get_nowait()

