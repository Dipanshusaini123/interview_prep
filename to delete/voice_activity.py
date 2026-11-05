
import numpy as np
import webrtcvad

from collections import deque
from math import gcd
from scipy.signal import resample_poly


class VoiceActivityDetector:
    """
    Detects candidate speech and automatically finishes
    a recording after a period of silence.

    Expected output:
        Raw PCM audio bytes (16 kHz, mono, int16).

    WAV conversion is handled separately by speech_to_text.py.
    """

    def __init__(
        self,
        sample_rate=16000,
        frame_duration_ms=30,
        silence_duration=1.5,
        max_recording_duration=60,
        vad_aggressiveness=2,
        pre_roll_duration=0.3
    ):

        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.silence_duration = silence_duration
        self.max_recording_duration = max_recording_duration
        self.pre_roll_duration = pre_roll_duration

        if frame_duration_ms not in (10, 20, 30):
            raise ValueError("Frame duration must be 10, 20 or 30 ms.")

        if sample_rate not in (8000, 16000, 32000, 48000):
            raise ValueError("Unsupported WebRTC VAD sample rate.")

        self.vad = webrtcvad.Vad(vad_aggressiveness)

        self.frame_samples = int(
            sample_rate * frame_duration_ms / 1000
        )

        self.silence_frames_required = int(
            silence_duration * 1000 / frame_duration_ms
        )

        self.max_frames = int(
            max_recording_duration * 1000 / frame_duration_ms
        )

        self.pre_roll_frames = int(
            pre_roll_duration * 1000 / frame_duration_ms
        )

        self.reset()

    def reset(self):
        """Reset detector for a new recording."""

        self.recording = False

        self.recorded_frames = []
        self.pre_roll = deque(maxlen=self.pre_roll_frames)

        self.silence_frames = 0
        self.total_frames = 0

        self.sample_buffer = np.array([], dtype=np.int16)

    def _convert_audio(self, audio_frame):
        """
        Convert PyAV audio frame into:
        16 kHz, mono, signed 16-bit PCM samples.
        """

        audio = audio_frame.to_ndarray()

        # Convert multi-channel audio to mono.
        if audio.ndim == 2:
            channels = len(audio_frame.layout.channels)

            if audio.shape[0] == channels:
                audio = audio.mean(axis=0)
            elif audio.shape[1] == channels:
                audio = audio.mean(axis=1)
            else:
                raise ValueError(
                    "Unable to determine audio channel layout."
                )

        audio = np.asarray(audio)

        # Convert samples into int16.
        if np.issubdtype(audio.dtype, np.floating):
            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)

        elif audio.dtype != np.int16:
            info = np.iinfo(audio.dtype)

            audio = (
                audio.astype(np.float64) / max(abs(info.min), info.max)
            )

            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)

        input_rate = audio_frame.sample_rate

        if not input_rate:
            raise ValueError("Audio frame has no sample rate.")

        # Resample to the target sample rate.
        if input_rate != self.sample_rate:

            common = gcd(input_rate, self.sample_rate)

            audio = resample_poly(
                audio,
                self.sample_rate // common,
                input_rate // common
            )

            audio = np.clip(
                audio, -32768, 32767
            ).astype(np.int16)

        return audio

    def _finish_recording(self):
        """
        Return completed recording as raw PCM bytes.
        """

        if not self.recorded_frames:
            self.reset()
            return None

        audio_bytes = b"".join(self.recorded_frames)

        self.reset()

        return audio_bytes

    def process_frame(self, audio_frame):
        """
        Process one incoming PyAV audio frame.

        Returns:
            bytes: Completed recording.
            None: Recording is still in progress.
        """

        audio = self._convert_audio(audio_frame)

        self.sample_buffer = np.concatenate(
            (self.sample_buffer, audio)
        )

        while len(self.sample_buffer) >= self.frame_samples:

            frame = self.sample_buffer[:self.frame_samples]

            self.sample_buffer = self.sample_buffer[
                self.frame_samples:
            ]

            frame_bytes = frame.tobytes()

            # Detect speech in the current audio frame.
            vad_speech = self.vad.is_speech(
                self.sample_rate,
                frame_bytes
            )

            rms = float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))

# Temporary debugging
            if not hasattr(self, "debug_counter"):
                self.debug_counter = 0

            self.debug_counter += 1

            if self.debug_counter % 25 == 0:
                print(
                    f"VAD DEBUG | "
                    f"RMS: {rms:.2f} | "
                    f"VAD Speech: {vad_speech}"
                )

            is_speech = vad_speech and rms >= 200
            # Candidate has started speaking.
            if is_speech and not self.recording:

                self.recording = True

                # Include a small amount of audio before speech.
                self.recorded_frames.extend(self.pre_roll)

                self.pre_roll.clear()

                print("Candidate started speaking.")

            # Store audio only after speech begins.
            if self.recording:

                self.recorded_frames.append(frame_bytes)

                self.total_frames += 1

                if is_speech:
                    self.silence_frames = 0
                else:
                    self.silence_frames += 1

                # Maximum recording duration reached.
                if self.total_frames >= self.max_frames:

                    print("Maximum recording duration reached.")

                    return self._finish_recording()

                # Candidate stopped speaking.
                if self.silence_frames >= self.silence_frames_required:

                    print("Silence detected. Recording completed.")

                    return self._finish_recording()

            else:
                # Maintain pre-roll audio before speech begins.
                self.pre_roll.append(frame_bytes)

        return None


def process_audio_frames(frames, detector):
    """
    Helper for processing multiple PyAV frames.

    Returns a list of completed recordings.
    """

    recordings = []

    for frame in frames:

        result = detector.process_frame(frame)

        if result:
            recordings.append(result)

    return recordings
