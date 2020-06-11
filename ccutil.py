import argparse
import json
import os
from pathlib import Path
import shutil


def parse_manifest(path):
    return json.load(open(os.path.join(path, "manifest")))


def extract_groups_handler(args):
    return extract_groups(args.cclib_folder, args.dest_folder)

def add_automatic_counter_to_filename(filename, extension):
    if not os.path.exists(filename + extension):
        return filename + extension
    new_filename = filename + extension
    index = 0
    while os.path.exists(new_filename):
        new_filename = filename + "#{}".format(index) + extension
        index += 1
    return new_filename

def extract_groups(cclib_folder, dest_folder):
    manifest = parse_manifest(cclib_folder)
    groups_manifest = [x for x in manifest["children"] if x["name"] == "groups"][0]
    groups = {group["id"]:group["name"] for group in groups_manifest["children"]}
    Path(dest_folder).mkdir(parents=True)
    for group_name in groups.values():
        Path(os.path.join(dest_folder, group_name)).mkdir()

    elements_manifest = [x for x in manifest["children"] if x["name"] == "elements"][0]
    elements = [{"name": element["name"],
                 "path": element["path"],
                 "group_name": groups[tuple(element["library#groups"].keys())[0].split("#")[-1]]
                 }
                for element in elements_manifest["children"]
                ]

    for element in elements:
        element_path = os.path.join(cclib_folder, element["path"])
        if not os.path.exists(element_path):
            continue
        element_folder = os.path.join(cclib_folder, element["path"])
        files = os.listdir(element_folder)
        for (i, file) in enumerate(files):
            filename = element["name"] + "_{}".format(i)
            dest_full_path = os.path.join(dest_folder, element["group_name"], filename)
            dest_full_path = add_automatic_counter_to_filename(dest_full_path, os.path.splitext(file)[-1])
            shutil.copyfile(os.path.join(element_folder, file), dest_full_path)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
extract_groups_parser = subparsers.add_parser('extract_groups', help="Extracts the CC library files in a heirarchy by groups")
extract_groups_parser.add_argument("cclib_folder", help="The cclib folder name (where the manifest file is located)")
extract_groups_parser.add_argument("dest_folder", help="The destination folder (where the manifest file is located)")
extract_groups_parser.set_defaults(func=extract_groups_handler)
args = parser.parse_args()
args.func(args)

