# Thanks to https://github.com/toashd/mozlz4/tree/master
# I simply converted the code to a python script and added the ability to output as markdown

import json
import lz4.block
import struct
import argparse

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

def create_md(json_dict: dict, links: list):
    if 'children' not in json_dict:
        return
    for child in json_dict['children']:
        if 'uri' in child and 'title' in child:
            links.append((child['title'], child['uri']))
        elif 'uri' in child:
            links.append((child['uri'], child['uri']))
        create_md(child, links)


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
        with open('bookmarks.md', 'w') as file:
            links = []
            create_md(decompressed_data, links)
            for link in links:
                file.write(f"[{link[0]}]({link[1]})\n\n")
    else:
        with open(output_path, 'w') as file:
            json.dump(decompressed_data, file, indent=4)

