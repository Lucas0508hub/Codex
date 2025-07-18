import collections
import contextlib
import wave
import webrtcvad

Frame = collections.namedtuple("Frame", ["timestamp", "data"])

def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n <= len(audio):
        yield Frame(timestamp, audio[offset:offset + n])
        timestamp += duration
        offset += n

def vad_collector(sample_rate, frame_duration_ms, padding_ms, vad, frames):
    num_padding_frames = int(padding_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []
    start_time = 0

    for frame in frames:
        is_speech = vad.is_speech(frame.data, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                start_time = ring_buffer[0][0].timestamp
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                end_time = frame.timestamp + frame_duration_ms / 1000.0
                yield start_time, end_time
                ring_buffer.clear()
                triggered = False
                voiced_frames = []
    if triggered:
        end_time = frames[-1].timestamp + frame_duration_ms / 1000.0
        yield start_time, end_time
