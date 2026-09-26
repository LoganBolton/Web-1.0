"""The Concord Reckoning calendar used across Averra.

* 10 months of 36 days, then 5 Hollowdays that belong to no month (365 days).
* 6-day week. Stillday is the rest day.
* Years are counted from the Treaty of the Nine Fords ("CR").
* The Kethren Holds count years from the founding of Harrowdeep instead
  ("HR"), where HR = CR + 880.

Each nation writes dates differently, which is deliberate.
"""
from dataclasses import dataclass

MONTHS = ["Rime", "Thaw", "Loam", "Bloom", "Blaze", "Crest", "Sheaf", "Gale", "Mire", "Dusk"]
WEEKDAYS = ["Anvilday", "Kettleday", "Loomday", "Plowday", "Hearthday", "Stillday"]
WEEKDAY_ABBR = ["Anv", "Ket", "Loo", "Plo", "Hea", "Sti"]
DAYS_IN_MONTH = 36
HOLLOWDAYS = 5
DAYS_IN_YEAR = 10 * DAYS_IN_MONTH + HOLLOWDAYS
HR_OFFSET = 880

# Season each month belongs to (the northern hemisphere of Averra).
MONTH_SEASON = {
    "Rime": "winter", "Thaw": "spring", "Loam": "spring", "Bloom": "spring",
    "Blaze": "summer", "Crest": "summer", "Sheaf": "autumn", "Gale": "autumn",
    "Mire": "autumn", "Dusk": "winter",
}


@dataclass(frozen=True, order=True)
class ADate:
    year: int
    month: int  # 1..10, or 11 for Hollowdays
    day: int    # 1..36 (1..5 for Hollowdays)

    # --- arithmetic -----------------------------------------------------
    def ordinal(self):
        return self.year * DAYS_IN_YEAR + (self.month - 1) * DAYS_IN_MONTH + (self.day - 1)

    @staticmethod
    def from_ordinal(n):
        year, rem = divmod(n, DAYS_IN_YEAR)
        month, day = divmod(rem, DAYS_IN_MONTH)
        return ADate(year, month + 1, day + 1)

    def __add__(self, days):
        return ADate.from_ordinal(self.ordinal() + days)

    def __sub__(self, other):
        if isinstance(other, ADate):
            return self.ordinal() - other.ordinal()
        return ADate.from_ordinal(self.ordinal() - other)

    # --- names ----------------------------------------------------------
    @property
    def month_name(self):
        return "Hollowday" if self.month == 11 else MONTHS[self.month - 1]

    @property
    def weekday(self):
        # Day 0 of year 0 (the signing of the Concord) was a Loomday.
        return WEEKDAYS[(self.ordinal() + 2) % 6]

    @property
    def weekday_abbr(self):
        return WEEKDAY_ABBR[(self.ordinal() + 2) % 6]

    @property
    def season(self):
        return "winter" if self.month == 11 else MONTH_SEASON[self.month_name]

    @property
    def hr_year(self):
        return self.year + HR_OFFSET

    # --- formats ----------------------------------------------------------
    def long(self):
        """'17 Gale 412' (the neutral, encyclopedic style)."""
        if self.month == 11:
            return f"Hollowday {self.day}, {self.year}"
        return f"{self.day} {self.month_name} {self.year}"

    def long_cr(self):
        return self.long() + " CR"

    def full(self):
        return f"{self.weekday}, {self.long()}"

    def veyl(self):
        """Concordat official numeric style: year·month·day."""
        return f"{self.year}·{self.month:02d}·{self.day:02d}"

    def salt(self):
        """Saltmarch style: day/month/year."""
        return f"{self.day}/{self.month}/{self.year}"

    def kethren(self):
        """Kethren style: day.month.HR-year, counted from Harrowdeep."""
        return f"{self.day}.{self.month}.{self.hr_year} HR"

    def pell(self):
        """Pellucid style: month name first."""
        return f"{self.month_name} {self.day}, {self.year}"

    def iso(self):
        """Machine format used in URLs and data files."""
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def by_nation(self, code):
        return {"VEY": self.veyl, "SLT": self.salt, "KHR": self.kethren,
                "PEL": self.pell}.get(code, self.long)()

    @staticmethod
    def parse_iso(s):
        y, m, d = s.split("-")
        return ADate(int(y), int(m), int(d))

    def __str__(self):
        return self.long()


# The "present day" of the world. Everything on the Weave is written as of now.
TODAY = ADate(412, 8, 17)  # Hearthday? computed: see TODAY.weekday
YEAR = TODAY.year


def month_days(year, month):
    return [ADate(year, month, d) for d in range(1, (HOLLOWDAYS if month == 11 else DAYS_IN_MONTH) + 1)]


def date_range(start, end):
    d = start
    while d <= end:
        yield d
        d = d + 1


def time_str(minutes):
    h, m = divmod(int(minutes) % (24 * 60), 60)
    return f"{h:02d}:{m:02d}"
