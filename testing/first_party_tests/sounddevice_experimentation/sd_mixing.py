import numpy
import sounddevice as sd

sd.default.channels = 2  # Default number of channels sd will attempt to use for input and output devices (I use 2 for Stereo audio.)
sd.default.dtype = 'int16'  # bit depth for a singular sample frame. pyFLAC currently only supports 16-bit audio, sd supports greater values.
sd.default.samplerate = 48000  # Sampling rate (how many samples frames to take per second) for audio data. higher value = greater audio depth, but larger performance overhead.
sd.default.blocksize = 256  # lower value = less latency, but more performance overhead

data_array = []
sample_num = input("Please input number of samples to take: ")
for sample in range(0, int(sample_num)):
    print(f"RECORDING TEST {sample+1}")
    data_array.append(sd.rec(3 * sd.default.samplerate))
    sd.wait()

finalmix = sum(data_array)
sd.play(finalmix)
sd.wait()
