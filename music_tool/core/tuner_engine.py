import numpy as np


class TunerEngine:
    def __init__(
        self,
        sample_rate=44100,
        buffer_size=2048,
        fmin=70,
        fmax=1000,
        threshold=0.1,
    ):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.fmin = fmin
        self.fmax = fmax
        self.threshold = threshold

        self.latest_frequency = None

    #  PUBLIC METHOD

    def process(self, audio_buffer):
        if len(audio_buffer) < self.buffer_size:
            return None

        audio_buffer = audio_buffer[: self.buffer_size]

        audio_buffer = audio_buffer - np.mean(audio_buffer)


        if np.sqrt(np.mean(audio_buffer**2)) < 0.01:
            return None

        tau = self._yin(audio_buffer)

        if tau is None:
            return None

        frequency = self.sample_rate / tau
        self.latest_frequency = frequency
        return frequency

    #  YIN CORE

    def _yin(self, x):
        N = len(x)
        max_tau = int(self.sample_rate / self.fmin)
        min_tau = int(self.sample_rate / self.fmax)

        # 1️ Difference function
        d = np.zeros(max_tau)
        for tau in range(1, max_tau):
            d[tau] = np.sum((x[:-tau] - x[tau:]) ** 2)

        # 2️ Cumulative mean normalized difference
        cmnd = np.zeros_like(d)
        cmnd[0] = 1
        running_sum = 0.0

        for tau in range(1, max_tau):
            running_sum += d[tau]
            cmnd[tau] = d[tau] * tau / running_sum if running_sum != 0 else 1

        # 3️⃣ Absolute threshold
        for tau in range(min_tau, max_tau):
            if cmnd[tau] < self.threshold:
                # 4️⃣ Parabolic interpolation
                return self._parabolic_interpolation(cmnd, tau)

        return None

    #  Interpolation

    def _parabolic_interpolation(self, cmnd, tau):
        if tau <= 0 or tau >= len(cmnd) - 1:
            return tau

        s0 = cmnd[tau - 1]
        s1 = cmnd[tau]
        s2 = cmnd[tau + 1]

        denom = 2 * (2 * s1 - s2 - s0)
        if denom == 0:
            return tau

        delta = (s2 - s0) / denom
        return tau + delta