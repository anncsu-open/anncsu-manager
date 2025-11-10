from typing import Callable, List, Optional
from whereabouts.Matcher import Matcher

class WhereaboutsGeocoder:
    """Wrapper class for the Whereabouts Matcher geocoder.
    Expose common geocoder interface methods."""
    def __init__(self, db_name: str, how: str, threshold: float):
        self.matcher = Matcher(db_name=db_name, how=how, threshold=threshold)

    def geocode(self, addresses: List[str]) -> List[dict]:
        return self.matcher.geocode(addresses=addresses)


class WhereaboutsGeocoderBuilder:
    """Builder class for WhereaboutsGeocoder to ensure singleton behavior
    and store geocoder creation in GoeocoderFactory."""
    def __init__(self):
        self._instance: Optional[WhereaboutsGeocoder] = None

    def __call__(self, matcher_db: str, how: str, threshold: float, **_ignored) -> WhereaboutsGeocoder:
        if not self._instance:
            self._instance = WhereaboutsGeocoder(matcher_db, how, threshold)
        return self._instance