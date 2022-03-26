import sounddevice as sd
import numpy

sd.default.samplerate = 48000
sd.default.channels = 2, 2
duration = 5 #seconds

print(f"Sound devices available to you are: \n {sd.query_devices()}\n")
input_Dev = int(input("Please enter the ID value of the input device you wish to use: "))
output_Dev = int(input("Please enter the ID value of the output device you wish to use: "))
sd.default.device = input_Dev, output_Dev
print(f"default devices set to: {sd.default.device}")

input("hit enter to test recording")
myrecording = sd.rec(int(duration * sd.default.samplerate))
sd.wait() # optional

input("Press enter to test playback")
sd.play(myrecording)
sd.wait()