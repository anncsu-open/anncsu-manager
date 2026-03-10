from typing import List, Optional
from geopy import geocoders
from geopy.geocoders.base import Geocoder

class GeopyGeocoder:
    """Wrapper class for the Geopy generic geocoder wrapper.
    Expose common geocoder interface methods."""
    def __init__(self, geocoder_class: Geocoder, **kwargs):
        # if kw_clean is in kwargs, remove al kw_clean listed keys from kwargs
        # before passing them to the geocoder constructor
        self.default_score: Optional[float] = kwargs.get('default_score', 0.0)
        if 'kw_clean' in kwargs:
            kw_clean = kwargs.pop('kw_clean')
            for key in kw_clean:
                kwargs.pop(key, None)
        self.geocoder = geocoder_class(**kwargs)

    def geocode(self, addresses: List[str]) -> List[dict]:
        geocoder_addresses = []
        for address in addresses:
            print(f"Geocoding address: '{address}'...")
            geocoded_location = self.geocoder.geocode(address)
            # avoid to use Location class to be more generic
            # and compatible with other goecoders
            if geocoded_location:
                geocoded_dict = {
                    'address': address,
                    'address_matched': geocoded_location.address,
                    'latitude': geocoded_location.latitude,
                    'longitude': geocoded_location.longitude,
                    'altitude': geocoded_location.altitude,
                    'similarity': getattr(geocoded_location, 'similarity', self.default_score),
                    'raw': geocoded_location.raw
                }
            else:
                print(f"WARNING! Address '{address}' could not be geocoded.")
                geocoded_dict = {
                    'address': address,
                    'address_matched': None,
                    'latitude': None,
                    'longitude': None,
                    'altitude': None,
                    'similarity': 0.0,
                    'raw': None
                }
            geocoder_addresses.append(geocoded_dict)
        return geocoder_addresses


class GeopyGeocoderBuilder:
    """Builder class for GeopyGeocoder to ensure singleton behavior
    and store geocoder creation in GoeocoderFactory."""
    def __init__(self):
        self._instances: dict[str, GeopyGeocoder] = {}

    def __call__(self, service_name: str, **kwargs) -> GeopyGeocoder:
        if service_name not in self._instances:
            geocoder_class = geocoders.get_geocoder_for_service(service_name)
            self._instances[service_name] = GeopyGeocoder(geocoder_class=geocoder_class, **kwargs)
        return self._instances[service_name]