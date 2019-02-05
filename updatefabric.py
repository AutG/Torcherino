import urllib.request as request
import xml.etree.ElementTree as ET
import sys
import string


class CustomTemplate(string.Template):
    delimiter = "@"


def main(args):
    mavenRepo = "https://maven.fabricmc.net/net/fabricmc/{}/maven-metadata.xml"
    templateargs = {}
    index = ""
    for value in args:
        if value[0] == "-":
            index = value[1::]
        else:
            templateargs[index] = value
            index = ""
    input_file = "template_build.gradle"
    output_file = "build.gradle"
    if "in" in templateargs:
        input_file = templateargs.pop("in")
    if "out" in templateargs:
        output_file = templateargs.pop("out")
    print("Downloading loom data")
    templateargs["fabric_loom_version"] = getReleaseOrLatest(mavenRepo.format("fabric-loom"))
    print("Downloading fabric data")
    templateargs["fabric_version"] = getReleaseOrLatest(mavenRepo.format("fabric"))
    print("Downloading fabric-loader data")
    templateargs["fabric_loader_version"] = getReleaseOrLatest(mavenRepo.format("fabric-loader"))
    print("Downloading yarn data")
    templateargs["minecraft_version"], templateargs["yarn_version"] = getReleaseOrLatest(mavenRepo.format("yarn")).split(".")
    print("Reading input file({0}).".format(input_file))
    with open(input_file, "r+") as f:
            templateContents = CustomTemplate(f.read())
    print("Saving to output file({0}).".format(output_file))
    with open(output_file, "w+") as f:
        f.write(templateContents.safe_substitute(templateargs))


def getReleaseOrLatest(mavenURL: str) -> str:
    mavenData = request.urlopen(mavenURL).read()
    elementTree = ET.fromstring(mavenData)
    version = elementTree.find("versioning/release")
    if version is not None:
        return version.text
    else:
        version = elementTree.find("versioning/versions")
        if version is not None:
            return version[-1].text
        else:
            raise ValueError("Maven doesnt have version data???")


if __name__ == "__main__":
    main(sys.argv[1::])