# create a generic factory to return geocoder instances based on configuration
from typing import Any, Dict, Optional
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager

class GeocoderFactory:

    builder: dict = {}

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(GeocoderFactory, cls).__new__(cls)
        return cls.instance

    def register_geocoder(self, geocoder_name: str, builder: Any) -> None:
        print(f"Registering geocoder {geocoder_name} with builder {builder}...")
        self._builders[geocoder_name] = builder

    def get_geocoder(self, geocoder_name: str, **kwargs: Dict[str, Any]) -> Optional[Any]:
        builder = self._builders.get(geocoder_name)
        if not builder:
            raise ValueError(geocoder_name)
        return builder(**kwargs)

    def reset_builders(self) -> None:
        self._builders = {}
