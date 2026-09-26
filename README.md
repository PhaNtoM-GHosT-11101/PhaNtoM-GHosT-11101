<div align="center">

# Aditya Priyadarshi

**B.Tech · Computational Mathematics**
National Institute of Technology Agartala

[![Python](https://img.shields.io/badge/Python-3B12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![MATLAB](https://img.shields.io/badge/MATLAB-E16737?logo=mathworks&logoColor=white)](https://www.mathworks.com/)

</div>

---

## Numerical methods & statistical inference

I care about methods that are **measured rather than assumed** — the order of
convergence of a solver, whether an interval really achieves its nominal
coverage, whether a hypothesis test controls its error rate. Both repositories
below are written to make those quantities checkable.

### [`numerical-methods-python`](numerical-methods-python)

Root-finding, ODE integration, optimisation and dense linear algebra in pure
NumPy, with every solver returning its full iteration history so convergence
order can be *measured*.

| Method | Measured order | Theory |
|---|---|---|
| Newton-Raphson | **1.98** | 2 |
| Secant | (two-step recurrence) | ~1.618 |
| Bisection | (envelope halves per step) | 1 |

Euler / Heun / RK4 on `y' = y` give implied orders **0.97 / 1.97 / 3.97**
against theory 1 / 2 / 4, measured by doubling the step count.

A recurring theme: a convergence *measurement* can itself be invalid, and the
tests pin down why. Bisection's error oscillates inside a halving envelope, so
no pointwise order estimate means anything; the secant recurrence
`e_n ~ C e_n e_{n-1}` is not of the form `e_{n+1} = C e_n^p`; and a
double-precision solver's final iterate sits *on* the noise floor, which drags
the mean order from 2.0 to 1.5 unless excluded.

`24/24 tests` · zero dependencies beyond NumPy

### [`monte-carlo-inference`](monte-carlo-inference)

Statistical inference in pure NumPy. No SciPy, no pandas, no statsmodels — the
distribution functions are implemented from scratch, so the mathematics stays
visible.

- Student-t via the regularised incomplete beta (Lentz continued fraction),
  reproducing published table values to `1e-5`
- Monte Carlo integration and importance sampling, with the optimal proposal
  `q ∝ f` driving the variance to zero
- Percentile bootstrap CIs; permutation test, **exact by enumeration** on small
  samples
- OLS with Student-t intervals and HC3 robust standard errors

The tests **measure error rates instead of trusting them**: 95% interval
coverage over hundreds of trials, permutation-test type I error under a true
null, and the CLT rate confirmed as `N**-0.5` rather than `N**-1` by showing
`|error| × √N` stays flat.

`28/28 tests` · Student-t table values match to `1e-5`

---

## Systems & tooling

Not the focus, but real projects I'd defend line by line.

| Project | What it is |
|---|---|
| [`reading-habit-app`](reading-habit-app) | Offline-first PWA EPUB reader. Bionic reading, dictionary lookup, cloud sync, community library. Offline-first sync with conflict resolution is the hard part. |
| [`phantom-player`](phantom-player) | Terminal music player in Python — `Textual` + `mpv`. No Electron. |
| [`WiFi-Watchdog`](WiFi-Watchdog) | Network reconnaissance in Shell: 639 lines, 26 functions, ARP-level discovery, MAC-randomisation detection, webhook alerting, table/CSV/JSON output. |

---

## Focus areas

Numerical analysis · Monte Carlo methods · Statistical inference · Optimization
· Time-series and stochastic processes

**Tooling:** Python (NumPy, pandas, matplotlib, pytest) · MATLAB · JavaScript · Shell · Git

---

<div align="center">
<sub>Building things that measure their own error. 📐</sub>
</div>
