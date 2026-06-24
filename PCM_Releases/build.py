
import os
from os import path
import shutil
import pathlib
import json
import sys
import fnmatch

src_path = path.join(path.dirname(__file__),'..')
version_path = path.join(path.dirname(__file__),'_version.py')
metadata_template = path.join(path.dirname(__file__),'metadata_template.json')
resources_path = path.join(path.dirname(__file__),'resources')
build_path = path.join('build')

# https://stackoverflow.com/a/6257321
def findReplace(directory, find, replace, filePattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            with open(filepath, 'rb') as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, 'wb') as f:
                f.write(s)

# Delete build content and recreate
try:
    shutil.rmtree(build_path)
except FileNotFoundError:
    pass
os.mkdir(build_path)
os.mkdir(path.join(build_path,'content'))
os.chdir(build_path)

# Copy symbols, footprints and 3dmodels
shutil.copytree(path.join(src_path,'symbols'), path.join('content','symbols'), dirs_exist_ok = True)
shutil.copytree(path.join(src_path,'footprints'), path.join('content','footprints'), dirs_exist_ok = True)
#shutil.copytree(path.join(src_path,'3dmodels'), path.join('content','3dmodels'), dirs_exist_ok = True)

# Replace every occurrence of "(model "${KICAD9_3RD_PARTY}/3dmodels/"
# with "(model "${KICAD10_3RD_PARTY}/3dmodels/alternate-kicad-library/"
#findReplace(path.join('content'), b'(model "${KICAD9_3RD_PARTY}/3dmodels/',
#    b'(model "${KICAD10_3RD_PARTY}/3dmodels/alternate-kicad-library/', '*.*')

# Copy icon
shutil.copytree(resources_path, path.join('content','resources'))

# Copy metadata
metadata = path.join('content','metadata.json')
shutil.copy(metadata_template, metadata)

# Load up json script
with open(metadata) as f:
    md = json.load(f)

# Get version from _version.py
# https://stackoverflow.com/a/7071358
import re
verstrline = open(version_path, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    verstr = "4.0.0"

# Update download URL
md['versions'][0].update({
    'version': verstr,
    'download_url': 'https://github.com/Li-Wenhui/Alternate-Kicad-Library/releases/download/v{0}/Alternate-Kicad-Library-{0}.zip'.format(verstr)
})

# Update metadata.json
with open(metadata, 'w') as of:
    json.dump(md, of, indent=2)

# Zip all files
zip_file = 'Alternate-Kicad-Library-{0}.zip'.format(md['versions'][0]['version'])
shutil.make_archive(pathlib.Path(zip_file).stem, 'zip', 'content')

# Rename the content directory so we can upload it as an artifact - and avoid the double-zip
shutil.move('content', 'Alternate-Kicad-Library-{0}'.format(md['versions'][0]['version']))
