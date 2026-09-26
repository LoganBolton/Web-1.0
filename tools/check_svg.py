"""Check every generated SVG parses as XML."""
import glob, sys
import xml.etree.ElementTree as ET
bad = 0
files = glob.glob(sys.argv[1] + "/**/*.svg", recursive=True)
for f in files:
    try:
        ET.parse(f)
    except ET.ParseError as e:
        bad += 1
        if bad < 15:
            print(f, e)
print(f"{len(files)} svg files, {bad} broken")
