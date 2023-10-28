# Thanks to https://github.com/toashd/mozlz4/tree/master
# I simply converted the code to a python script and added the ability to output as markdown

import argparse
import json
import logging
import struct
from io import TextIOWrapper

import lz4.block

# Custom Mozilla LZ4 file header / magic number
MAGIC_NUMBER = "mozLz40\0"

def decompress(input_buffer):
    # Verify input_buffer
    if not isinstance(input_buffer, bytes):
        raise ValueError('input is not of type bytes')

    # Verify custom Mozilla LZ4 header
    if input_buffer[:8].decode('utf-8') != MAGIC_NUMBER:
        raise ValueError('input does not seem to be a valid jsonlz4 format')

    output_size = struct.unpack('<I', input_buffer[8:12])[0]
    output_buffer = lz4.block.decompress(input_buffer[12:], uncompressed_size=output_size)
    return json.loads(output_buffer.decode('utf-8'))

def write_md(json_dict: dict, file: TextIOWrapper, depth=1):
    if 'children' not in json_dict:
        return
    for idx, child in enumerate(json_dict['children']):
        if not 'uri' in child:
            file.write(f"{'#'*(depth+1)} {child['title']}\n\n")
        write_md(child, file, depth=depth+1)
        if 'uri' in child and 'title' in child:
            file.write(f"[{child['title']}]({child['uri']})\n")
        elif 'uri' in child:
            links.append(f"[{child['uri']}]({child['uri']})\n")
    file.write("\n")
    


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="mozilla jsonlz4 decompression")

    p.add_argument(
        "-m", "--markdown",
        action="store_true",
        help="Output as markdown instead of json"
    )
    p.add_argument(
        "input",
        type=str,
        help="Path to input file"
    )
    p.add_argument(
        "output",
        type=str,
        help="Path to output file"
    )

    args: argparse.Namespace = p.parse_args()

    input_path = args.input
    output_path = args.output

    with open(input_path, 'rb') as file:
        decompressed_data = decompress(file.read())

    if args.markdown:
        # TODO: Visualize folders
        if output_path[-3:] != ".md":
            logging.warning("Output file does not end with .md")
        with open(output_path, 'w') as file:
            file.write("# Bookmarks\n\n")
            write_md(json_dict=decompressed_data, file=file)
    else:
        if output_path[-5:] != ".json":
            logging.warning("Output file does not end with .json")
        with open(output_path, 'w') as file:
            json.dump(decompressed_data, file, indent=4)

