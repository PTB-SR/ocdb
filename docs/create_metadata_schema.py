import ocdb.io

FILENAME = "metadata-schema.yaml"

metadata = ocdb.io.Metadata()
metadata.versions.append(ocdb.io.VersionMetadata())
metadata.references.append("")
ocdb.io.create_metadata_file(filename=FILENAME)
