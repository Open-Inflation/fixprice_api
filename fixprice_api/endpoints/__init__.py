from . import advertising as _advertising
from . import catalog as _catalog
from . import general as _general
from . import geolocation as _geolocation

ClassCatalog = _catalog.ClassCatalog
ClassGeolocation = _geolocation.ClassGeolocation
ClassAdvertising = _advertising.ClassAdvertising
ClassGeneral = _general.ClassGeneral

__all__ = [
    "ClassCatalog",
    "ClassGeolocation",
    "ClassAdvertising",
    "ClassGeneral",
]
