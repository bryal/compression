#!/usr/bin/python3

import scipy.io.wavfile
import numpy
from numpy.fft import rfft, irfft
import sys

def compress(filename):
    sample_rate, samples = scipy.io.wavfile.read(filename)
    channels = samples.T
    ft = [x for x in map(rfft, channels)]
    original_ft_len = len(ft[0])
    high_cut = map(lambda l: numpy.complex64(l[0:len(l)//4]), ft)

    out_filename = filename + ".compressed"
    with open(out_filename, "wb") as out:
        out.write(sample_rate.to_bytes(4, byteorder="big"))
        out.write(original_ft_len.to_bytes(4, byteorder="big"))
        for compressed in high_cut:
            out.write(compressed.tobytes())

def uncompress(filename):
    with open(filename, "rb") as f:
        sample_rate = int.from_bytes(f.read(4), "big")
        original_ft_len = int.from_bytes(f.read(4), "big")
        shortened_len = original_ft_len // 4
        channel_n_bytes = shortened_len * 8
        pad_width = original_ft_len - shortened_len
        compr_bytes = [f.read(channel_n_bytes), f.read(channel_n_bytes)]
        high_cut = map(lambda bs: numpy.fromstring(bs, dtype=numpy.complex64), compr_bytes)
        padded = map(lambda l: numpy.pad(l, (0, pad_width), "constant"), high_cut)
        channels = map(irfft, padded)
        rounded = numpy.around([x for x in channels])
        uncompressed_samples = numpy.array(rounded, dtype=numpy.int16).T

        out_filename = filename + ".uncompressed.wav"
        scipy.io.wavfile.write(out_filename, sample_rate, uncompressed_samples)


args = sys.argv

def print_usage():
    print("Usage: {} OPERATION FILE\nOPERATION=c => Compress\nOPERATION=u => Uncompress", args[0])

if len(args) == 3:
    if args[1] == "c":
        compress(args[2])
    elif args[1] == "u":
        uncompress(args[2])
    else:
        print_usage()
else:
    print_usage()
