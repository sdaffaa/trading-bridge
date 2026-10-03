"""US holiday / early-close calendar for COMEX-linked gold trading (published in advance,
so using it is NOT look-ahead). Approximation to verify against the broker's schedule:
on these trading days the session may end early (~13:00-13:30 NY) or not trade at all.
Strategies treat them as early-close days: no entries after 11:00 NY, flat from 12:00 NY.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar, GoodFriday, AbstractHolidayCalendar


class _GF(AbstractHolidayCalendar):
    rules = [GoodFriday]


def early_close_dates(start="2000-01-01", end="2035-12-31") -> set:
    fed = USFederalHolidayCalendar().holidays(start, end)
    gf = _GF().holidays(start, end)
    years = range(pd.Timestamp(start).year, pd.Timestamp(end).year + 1)
    thanks = [d for d in fed if d.month == 11 and d.day >= 22]
    extra = [d + pd.Timedelta(days=1) for d in thanks]                     # day after Thanksgiving
    extra += [pd.Timestamp(y, 12, 24) for y in years] + [pd.Timestamp(y, 12, 31) for y in years]
    return {d.date() for d in list(fed) + list(gf) + extra}


_EARLY = early_close_dates()


def is_early_close_day(trading_days: np.ndarray) -> np.ndarray:
    return np.array([d in _EARLY for d in trading_days], dtype=bool)
