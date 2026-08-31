#!/usr/bin/env bash

set -euo pipefail

SCHEMA_FILE="$GITHUB_WORKSPACE/orca/share/glib-2.0/schemas/org.gnome.Orca.gschema.xml"
OUTPUT_FILE="$GITHUB_WORKSPACE/guidepup.ini"

if [[ ! -f "$SCHEMA_FILE" ]]; then
    echo "ERROR: Schema file not found: $SCHEMA_FILE" >&2
    exit 1
fi

python3 - "$SCHEMA_FILE" "$OUTPUT_FILE" <<'PY'
import sys
import xml.etree.ElementTree as ET

schema_file = sys.argv[1]
output_file = sys.argv[2]

root = ET.parse(schema_file).getroot()

prefix = "org.gnome.Orca."

with open(output_file, "w", encoding="utf-8") as out:
    for schema in root.findall("schema"):
        schema_id = schema.attrib["id"]

        if not schema_id.startswith(prefix):
            raise ValueError(
                f"Unexpected schema ID: {schema_id}"
            )

        # org.gnome.Orca.CaretNavigation
        # -> caret-navigation
        name = schema_id[len(prefix):]

        path_name = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                path_name.append("-")
            path_name.append(char.lower())

        path = "".join(path_name)

        out.write(f"[/org/gnome/orca/guidepup/{path}/]\n")

        for key in schema.findall("key"):
            key_name = key.attrib["name"]
            default = key.find("default")

            if default is None:
                raise ValueError(
                    f"{schema_id}:{key_name} has no <default>"
                )

            value = default.text or ""

            out.write(f"{key_name}={value}\n")

        out.write("\n")

print(f"Generated: {output_file}")
PY