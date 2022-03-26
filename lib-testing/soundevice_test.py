import sounddevice as sd
import pyogg
import numpy
import math

sd.default.samplerate = 48000 #48Khz sampling rate
sd.default.channels = 2, 2 #2 channels for input two channels for output

print(f"Sound devices available to you are: \n {sd.query_devices()}\n")
input_Dev = int(input("Please enter the ID value of the input device you wish to use: "))
output_Dev = int(input("Please enter the ID value of the output device you wish to use: "))
sd.default.device = input_Dev, output_Dev
print(f"default devices set to: {sd.default.device}")

input("hit enter to test recording... ")
testrecording = sd.rec(int(1 * sd.default.samplerate))
print("RECORDING")
sd.wait()  # optional

input("Press enter to test playback... ")
sd.play(testrecording)
print("PLAYING")
sd.wait()


