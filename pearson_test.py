import numpy as np
from scipy.stats import chisquare, norm, chi2


class NormPearsonChiSquaredTest:
    def __init__(self, filename: str, n_intervals: int, alpha: float):
        try:
            with open(filename, 'r') as fin:
                lines = fin.readlines()
            self.samples = np.array([float(line.strip().replace(',', '.')) for line in lines])
        except Exception:  # noqa
            raise BadInput
        self.n_intervals = n_intervals
        self.alpha = alpha
        self.ddof = self.n_intervals - 2 - 1
        self.hist, self.bins = None, None
        self.stats = dict()

    def _calc_stats(self) -> dict:
        if self.hist is None or self.bins is None:
            raise ValueError('Props hist and/or bins not set. Call evaluate_chisq first.')
        if self.stats:
            return self.stats
        self.stats['mean'] = np.mean(self.samples)
        self.stats['std'] = np.std(self.samples)
        self.stats['var'] = np.var(self.samples)
        self.stats['std2'] = self.stats['std'] * len(self.samples) / (len(self.samples) - 1)
        self.stats['mids'] = [(self.bins[i] + self.bins[i + 1]) / 2.0 for i in range(len(self.bins) - 1)]
        sample_mean = sum((x_i * n_i for x_i, n_i in zip(self.stats['mids'], self.hist))) / len(self.samples)
        sample_var = np.sqrt(sum((x_i**2 * n_i for x_i, n_i in zip(self.stats['mids'], self.hist))) / len(self.samples) - sample_mean**2)

        z = [(x - sample_mean) / sample_var for x in self.stats['mids']]
        gauss = norm.pdf(z)
        self.h = self.bins[1] - self.bins[0]
        self.n_dash_list = [(self.h * len(self.samples) / sample_var) * gauss_i for gauss_i in gauss]
        self.chisq = sum(((n_i - n_dash_i)**2 / n_dash_i for n_i, n_dash_i in zip(self.hist, self.n_dash_list)))
        self.chisq_crit = chi2.ppf(1 - self.alpha, self.ddof)

    def evaluate_chisq(self) -> bool:
        self.hist, self.bins = np.histogram(self.samples, self.n_intervals)
        self._calc_stats()
        return self.chisq > self.chisq_crit


class BadInput(Exception):
    pass


if __name__ == '__main__':
    for i in range(10**6):
        print('DAMN SON WHERE DID YOU FIND THIS ? ? ? ? ? ?')
