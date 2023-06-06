from dataclasses import dataclass


@dataclass
class Constants:
    radius: int = 6.4E6
    heat_capacity: int = 1e5
    albedo: float = 0.3
    solar: int = 1370


@dataclass
class Configuration:
    points: int = 1500
    res: int = 75
    dt: int = 18 * 60
    day: int = 60 * 60 * 24

    def year(self):
        return 365.25 * self.day


@dataclass
class Settings:
    resolution: int = 75
