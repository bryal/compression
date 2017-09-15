#!/usr/bin/python3

import scipy.io.wavfile
import numpy
from numpy.fft import rfft, irfft
import sys

def compress(filename):
    sample_rate, samples = scipy.io.wavfile.read(filename)
    left, right = samples.T
    left_ft, right_ft = rfft(left), rfft(right)
    original_ft_len = len(left_ft)
    left_ft_high_cut = numpy.complex64(left_ft[0:original_ft_len//4])
    right_ft_high_cut = numpy.complex64(right_ft[0:original_ft_len//4])

    out_filename = filename + ".compressed"
    with open(out_filename, "wb") as out:
        out.write(sample_rate.to_bytes(4, byteorder="big"))
        out.write(original_ft_len.to_bytes(4, byteorder="big"))
        out.write(left_ft_high_cut.tobytes())
        out.write(right_ft_high_cut.tobytes())

def uncompress(filename):
    with open(filename, "rb") as f:
        sample_rate = int.from_bytes(f.read(4), "big")
        original_ft_len = int.from_bytes(f.read(4), "big")
        shortened_len = original_ft_len // 4
        channel_n_bytes = shortened_len * 8
        left_bytes = f.read(channel_n_bytes)
        right_bytes = f.read(channel_n_bytes)
        left_ft_high_cut = numpy.fromstring(left_bytes, dtype=numpy.complex64)
        right_ft_high_cut = numpy.fromstring(right_bytes, dtype=numpy.complex64)
        pad_width = original_ft_len - shortened_len
        left_ft_padded = numpy.pad(left_ft_high_cut, (0, pad_width), "constant")
        right_ft_padded = numpy.pad(right_ft_high_cut, (0, pad_width), "constant")
        left, right = irfft(left_ft_padded), irfft(right_ft_padded)
        uncompressed_samples = numpy.array(numpy.around([left, right]), dtype=numpy.int16).T

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
