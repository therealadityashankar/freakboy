"""all functions in freakboy"""
import random
import struct
import array
import math
import numpy as np
from freakboy.error import Error


def data_for_freq(
    frequency,
    frame_count,
    amplitude=1,
    sampling_rate=44100,
    number_of_channels=2,
    wave_type="sine",
):
    """
    displacement of particles happens in a sine wave in this function

    get frames for a fixed frequency for a specified time or
    number of frames, if frame_count is specified, the specified
    time is ignored

    Returns
    ----------
    bytes
        for generating fixed frequency and amplitude in
        pyaudio format

    last_position
        the last posit
    Parameters
    ----------
    frequency: float
        frequency required
    sampling_rate: int
        sampling rate for audio
    sample_width: int
        width of a sample in bytes
        1 is a char
        2 is a short int
        ...
        unsigned values are not accepted
    number_of_channels : int
        number of channels in wave
    frame_count: int, optional
        number of frames to return (has preference over time)
        time or frame_count must be specified
        if none defaults to number_of_channels*sampling_rate,
        i.e. data for 1 second of audio
    offset: float
        a number between 0 and 1
        sine waves normally start at sin(0)
        specifing an offset will make them start at sin(offset*2*PI)
    amplitude: float or callable
        float
            a number between 0 and 1
            specifies the amplitude of the returned data

        callable
            Parameters
            --
            position
                a number between 0 and 1 determining the position
                of the given frame, 0 is the beginning, 1 is the end
    wave_type: string
        the type of the wave wanted,
        'sine' or 'square' are supported

            Returns
            --
                a number between 0 and 1 determining the amplitude
    """
    wavedata = []
    frequency_callable = callable(frequency)
    amplitude_callable = callable(amplitude)
    for i in range(frame_count):
        position_in_frames = i / frame_count
        if frequency_callable:
            frames_per_wave = sampling_rate / frequency(position_in_frames)
        else:
            frames_per_wave = sampling_rate / frequency

        position_in_wave = i / frames_per_wave

        if wave_type == "sine":
            displacement = msin(position_in_wave)
        elif wave_type == "square":
            displacement = square(position_in_wave)
        else:
            raise Error("invalid wave type :" + wave_type)

        displacement = displacement * 32767
        if amplitude_callable:
            displacement = displacement * amplitude(position_in_frames)
        else:
            displacement = displacement * amplitude
        displacement = int(displacement)
        for _ in range(number_of_channels):
            wavedata.append(displacement)

    return wavedata


def combine_data(*datas, average=True):
    """
    combines data by averaging it

    Parameters
    ----------
    an infinite number of data parameters
    """
    new_data = []
    for data in datas:
        for i, num in enumerate(data):
            if i < len(new_data):
                value = new_data[i] + data[i]
                new_data[i] = value
            else:
                num = data[i]
                new_data.append(num)

    if average:
        for i, num in enumerate(new_data):
            num_of_datas = len(datas)
            new_data[i] = int(num / num_of_datas)

    return new_data


def pack_data(data, data_width):
    """
    packs data into bytes

    Parameters
    ----------
    data : list
        numeric list of data

    data_width : int
        width in bytes of each piece of data
        currently only supports a width of 2
        only signed numbers are supported
    """
    if data_width != 2:
        raise Error("currently only a data width of 2 is supported")
    number_of_bytes = str(len(data))
    wavedata = struct.pack(number_of_bytes + "h", *data)
    return wavedata


def freq_of_key(key_number):
    """determines the frequency of the 12th key of a piano
    middle c is key 40, the next c# or d minor is 41,
    the previous b is 39
    the rest of the keys follow a similar pattern

    Parameters
    ----------
    key_number: int
        frequency of key wanted

    Returns
    ---------
    frequency: float
        frequency of deszired key
    """
    k = 1.0594630943592953
    l = k ** (key_number - 49)
    frequency = l * 440
    return frequency


def width_to_typecode(width):
    """
    returns corresponding typecode for width
    """
    pass


def mapper(val, i_from, i_till, f_from, f_till):
    """
    maps a value
    val that varies
    from i_from -> i_till
    to f_from -> f_till
    """
    i_len = i_till - i_from
    f_len = f_till - f_from
    val_ratio = (val - i_from) / i_len
    mapped_val = val_ratio * f_len + f_from
    return mapped_val


def msin(x, half=False):
    """
    mapped half sine wave
    same as math.sin(math.pi*x) for a half sin wave
         and math.sin(2*math.pi*x) for a full sin wave
    Parameters
    ----------
    x : float
        position of the wave who mapped half sine value is required
    """
    if half:
        val = math.sin(math.pi * x)
    else:
        val = math.sin(2 * math.pi * x)
    return val


def square(x):
    """
    replicates a square wave
    """
    x = x - int(x)
    if x < 0.5:
        return 1
    else:
        return -1


def tri(x, increment_till=0.5):
    """
    value raises from -1 to 1
    for the x value of 0 till increment_till linearly,
    then drops the value from 1 to -1 for
    increment_till to 1
    """
    if x < increment_till:
        val = x / increment_till
    else:
        x = 1 - x
        dec_len = 1 - increment_till
        val = x / dec_len
    val = mapper(val, 0, 1, -1, 1)
    return val


def mexp(x, min_val=0.001, raises=False):
    """
    raises or depletes based on
    raises = True or False
    from min_val to 1 or vice-versa
    exponentially for value between 0 to 1
    """
    val_extension = math.log(min_val)
    if raises:
        x = 1 - x
    val = math.exp(x * val_extension)
    return val


def rand(x, min_val=1000, max_val=20000):
    """
    returns a random number between min_val and max_val
    """
    val = random.uniform(min_val, max_val)
    return val
