"""
player class in freakboy
"""
import numpy
import random
import pyaudio

from freakboy.error import Error
import freakboy.functions as defs


class Player:
    """
    creates a player that plays frequencies async
    """

    def __init__(self,
                 pyaudio_ins=None,
                 sample_width=2,
                 sampling_rate=44100,
                 channels=2):
        """
        play frequencies async

        Parameters
        ----------
        pyaudio_ins
            an instance of pyaudio.PyAudio()
        sample_width : int
            ranges from 1 to 4, both inclusive,
            width of each sample in bytes,
            all values are signed
        sampling_rate : int
            number of samples per second
        channels : int
            number of channels
            1 for mono
            2 for stereo

        Returns
        ---------
        an instance of this class
        """
        if pyaudio_ins is not None:
            self.pyaudio_ins = pyaudio_ins
            self.pyaudio_ins_created = False
        else:
            self.pyaudio_ins = pyaudio.PyAudio()
            self.pyaudio_ins_created = True

        self.sample_width = sample_width
        self.channels = channels
        self.sampling_rate = sampling_rate

        self.data = []

    def add(self, *data):
        """adds data to self.data

        Parameters
        ----------
        data : AudioData instance
            instance of AudioData
        """
        self.data += list(data)

    def get_numeric_data(self):
        """returns numbers corrosponding to released audio"""
        # apiece -> audio piece
        amp_reduction_factor = len(self.data)
        apiece_lens = [len(apiece.data) for apiece in self.data]
        max_apiece_len = max(apiece_lens)

        # since only a sample width of 2 is supported
        numpy_data_type = numpy.int16
        numeric_data = numpy.zeros(max_apiece_len, dtype=numpy_data_type)

        for apiece in self.data:
            curr_data = apiece.data
            curr_data_len = len(apiece)

            numeric_data[0: curr_data_len] += curr_data
        return numeric_data

    def get_byte_data(self):
        numeric_data = self.get_numeric_data()
        data = numeric_data.tobytes()
        return data

    def get_audio(self):
        """retrieves recording"""

        recording = {
            'sample_rate': self.sampling_rate,
            'channels': self.channels,
            'sample_width': self.sample_width,
            'recording_values': self.get_byte_data()
        }

        return recording

    def play(self):
        """plays audio"""
        audio = self.get_audio()
        pyaudio_format = pyaudio.get_format_from_width(audio['sample_width'])

                                       channels=audio['channels'],
                                       format=pyaudio_format,
                                       output=True)
        stream.close()

    def close(self):
        """
        closes the audio stream
        """
        if self.pyaudio_ins_created:
            self.pyaudio_ins.terminate()

    def __del__(self):
        """
        on deletion
        """
        self.close()


class AudioData:
    """
    audio data class

    defines a chunck of audio data
    """

    def __init__(self,
                 pre_frame_count=0,
                 data=None,
                 sample_width=2,
                 channels=2,
                 sampling_rate=44100):
        """
        creates an audio chunk

        Parameters
        ----------
        pre_frame_count : int
            number of empty frames before this AudioData
            piece
        data : list
            data as a list of numbers
            data defaults to [] if none
        sample_width : int
            ranges from 1 to 4, both inclusive,
            width of each sample in bytes,
            all values are signed
        sampling_rate : int
            number of samples per second
            only a sample with of 2 is currently supported

        channels : int
            number of channels
            1 for mono
            2 for stereo

        Returns
        ---------
        an instance of this class
        """
        # values
        self.sample_width = sample_width
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.key_play_style = defs.mexp
        # checks
        self.check_sample_width()

        # data
        data = data or []

        numpy_sample_type = self.get_numpy_sample_type(sample_width)

        data_len = pre_frame_count + len(data)

        self.data = numpy.zeros(data_len,
                                dtype=numpy_sample_type)
        self.data[pre_frame_count:] = data

    def check_sample_width(self):
        """
        checks the sample width
        currently only supports a width of 2
        """
        if self.sample_width != 2:
            raise Error('currently only a sample width of 2\
                            is supported !')

    def get_numpy_sample_type(self, sample_width):
        """
        gets the numpy sample type for the value
        """
        if sample_width == 2:
            return numpy.int16

        else:
            raise Error('only a sample width of 2 is currently supported')

    def add_data(self, data):
        """adds data to this audio_data chunk

        Parameters
        ----------
        data : list of data to add to existing data
        """
        sample_width = self.sample_width
        numpy_sample_type = self.get_numpy_sample_type(sample_width)
        data = numpy.array(data, dtype=numpy_sample_type)
        data_len = len(self) + data.size
        old_data_len = len(self)

        new_data = numpy.empty(data_len, numpy_sample_type)
        new_data[0: old_data_len] = self.data
        new_data[old_data_len:] = data
        self.data = new_data

    def clear(self):
        """
        clears all data within
        """
        self.data = []

    def time_to_frames(self, for_time):
        """
        convert time to frame count

        Parameters
        ----------
        time : float
            time in seconds
        """
        frame_count = (self.sampling_rate * for_time)
        return frame_count

    def frame_count_to_time(self, frame_count):
        """
        convert frame_count to time

        Parameters
        ----------
        frame_count : int
            the frame count to turn into time
        """

        time = frame_count / self.sampling_rate
        return time

    def _get_frames(self, for_time=None, frame_count=None):
        """
        gets the correct number of frames

        frame_count is given significance
        Parameters
        ----------
        for_time : float, optional
            time in seconds

        frame_count : int
            number of frames
        """
        if frame_count is None:
            try:
                frame_count = self.time_to_frames(for_time)

            except TypeError:
                if for_time is None:
                    raise \
                        Error("for_time or \
                               frame_count must be specified")

        return frame_count

    def __len__(self):
        return self.data.size

    def add_sound(
            self,
            frequency,
            amplitude,
            for_time=None,
            frame_count=None):
        """
        async callback for stream

        Parameters
        ----------
        frame_count : int
            number of frames
            frame_count or for_time must be specified

        for_time : float
            amount of time the sound should play for
            frame_count or for_time must be specified

        frequency : float or callable or None
            frequency of the sound

            for None:
                default self.frequency is used

            for float:
                number representing the frequency

            for callable:
                Parameters
                ----------
                position : float
                    number between 0 and 1
                    representing the position of the
                    frame in frame count
                    so 325th frame out of the 1000th
                    has position 0.325
                    (floating point errs occur)

                Returns
                -------
                frequency wanted at position

        amplitude : float or callable
            amplitude of the sound

            for None:
                default self.amplitude is used

            for float:
                number representing the frequency

            for callable:
                Parameters
                ----------
                position : float
                    number between 0 and 1
                    representing the position of the
                    frame in frame count
                    so 325th frame out of the 1000th
                    has position 0.325
                    (floating point errs occur)

                Returns
                -------
                amplitude wanted at position
        """
        frame_count = self._get_frames(for_time, frame_count)

        frame_count = int(frame_count)

        data = defs.data_for_freq(frequency=frequency,
                                  frame_count=frame_count,
                                  amplitude=amplitude,
                                  sampling_rate=self.sampling_rate,
                                  number_of_channels=self.channels)

        self.add_data(data)

    def play_key(self,
                 key_number,
                 harmonic_time=None,
                 play_function=None,
                 harmonic_frames=None,):
        """
        plays a key

        Parameters
        ----------

        key_number: float or int
            key number of the key to be played
            middle c is 40

        harmonic_time: float, optional
            length of the beat in seconds
            harmonic_time or harmonic_frames must be
            specified

        harmonic_frames : int, optional
            number of frames for the beat to last for
            harmonic_time or harmonic_frames must be
            specified

        play_function: Callable
            a function that varies the amplitude
        """
        if play_function is None:
            play_function = self.key_play_style

        frequency = defs.freq_of_key(key_number)
        self.add_sound(for_time=harmonic_time,
                       frame_count=harmonic_frames,
                       frequency=frequency,
                       amplitude=play_function)

    def drum_snare(self, time=None, frame_count=None):
        """
        replicates a drum snare

        see Player.add_sound() for the meaning of the
        parameters
        """
        min_freq = 1000
        max_freq = 20000

        def rand(position):
            return random.uniform(min_freq, max_freq)

        self.add_sound(for_time=time,
                       frame_count=frame_count,
                       frequency=rand,
                       amplitude=defs.mexp)

    def add_silence(self, time=None, frame_count=None):
        """
        add silence to the data sequence

        see Player.add_sound() for the meaning of the
        parameters
        """
        self.add_sound(1, 0, time, frame_count)

    def clone(self):
        """
        clones itself
        """
        cloned_self = AudioData(data=self.data[:],
                                sample_width=self.sample_width,
                                channels=self.channels,
                                sampling_rate=self.sampling_rate)

        return cloned_self
