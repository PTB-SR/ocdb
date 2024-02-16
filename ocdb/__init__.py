"""ocdb

Optical constants for elements and various materials in the EUV and VUV
wavelengths.
"""

__all__ = []

import sys

from . import management
from . import material

materials = material.Collection()

for collection_name in ["elements", "compositions"]:
    collection_creator = management.CollectionCreator()
    collection = collection_creator.create(name=collection_name)
    setattr(sys.modules[__name__], collection_name, collection)
    __all__.append(collection_name)

    for item in collection:
        materials.add_item(item)

del collection_name, collection_creator, collection
