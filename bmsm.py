import json
import yaml
from sys import argv


class header:
    def __init__(self):
        self.string_count: str
        self.file_type: int


class bmsm:
    def __init__(self, filename: str):
        self.file = open(filename, "rb+")
        self.filename = filename
        self.header = header()
        self.header.string_count = int(
            "".join([self.file.read(1).hex() for i in range(4)][::-1]), 16
        )
        self.header.file_type = int(
            "".join([self.file.read(1).hex() for i in range(1)][::-1]), 16
        )
        if self.header.file_type != 6:
            raise Exception(
                f"The file provided is not a valid BMSM file. The header is equal to {self.header.file_type}"
            )

    def read_message(self) -> bytes:
        count = 0
        message = b""
        byte = self.file.read(2)
        while count != 1:
            byte = self.file.read(2)
            if byte == b"\x00\x00":
                count += 1
            else:
                message += byte
                count = 0

        return message.decode("UTF-16")

    def read_label_unkown_data(self) -> list:
        label_data = b""
        count = 0
        byte = self.file.read(1)
        while count != 1:
            label_data += byte
            byte = self.file.read(1)
            if byte == b"\xff" or byte == b"\xfe":
                count += 1
        return [i for i in label_data.split(b"\x00") if len(i) != 0]

    def parse(self):
        entries = {}
        entries[self.filename] = {}
        self.file.seek(8)
        for _ in range(self.header.string_count):
            # Call this unknown data as we don't know what the other
            # entries are for other than the text-label
            unknown_data = self.read_label_unkown_data()
            # Seek before the text-start identifer for utf-16 reading
            self.file.seek(self.file.tell() - 1)
            message = self.read_message()
            # Label data can be length of 2 without the unknown entries or length of 5 with the unknown entries
            label = (
                unknown_data[0].decode("ASCII")
                if len(unknown_data) != 5
                else unknown_data[3].decode("ASCII")
            )

            print("Parsing entry:", {label: message})

            if len(unknown_data) != 2:
                unknown_data.remove(label.encode("ASCII"))
            entries[self.filename][label] = {"Message": message}
            for encoded_unknown in range(len(unknown_data)):
                try:
                    unknown_data[encoded_unknown] = unknown_data[
                        encoded_unknown
                    ].decode("ASCII")
                except:
                    pass
            if len(unknown_data) > 2:
                entries[self.filename][label] = {
                    "BMSS Style Label": unknown_data[len(unknown_data) - 1],
                    "Unknowns": sorted(
                        [
                            unknown_data[len(unknown_data) - 2],
                            unknown_data[len(unknown_data) - 3],
                            unknown_data[len(unknown_data) - 4],
                        ],
                        key=len,
                    )[::-1],
                    "Message": message,
                }
            else:
                entries[self.filename][label] = {
                    "BMSS Style Label": unknown_data[len(unknown_data) - 1],
                    "Unknowns": [],
                    "Message": message,
                }
        return entries

    def to_json(self, json_filename: str):
        with open(json_filename, "w+") as file:
            json.dump(self.parse(), file, indent=4)

    def to_yaml(self):
        with open(f"{self.filename[:-5]}.yaml", "w+") as file:
            yaml.dump(self.parse(), file)

    def from_json(self, exported_file) -> None:
        self.file.seek(0)
        bmsm_data = json.loads(open(exported_file, "r").read())
        bmsm_data = bmsm_data[self.filename]
        with open(f"{self.filename}", "rb+") as bmsm_file:
            bmsm_file.write(
                len(bmsm_data).to_bytes(4, byteorder="little", signed=False)
            )
            bmsm_file.write(b"\x06\x00\x00\x00")

            def next_key(dict, key):
                keys = iter(dict)
                key in keys
                return next(keys)

            for key in bmsm_data:
                print("Writing entry", bmsm_data[key])
                bmsm_file.write(key.encode())
                bmsm_file.write(b"\x00")
                bmsm_file.write(bmsm_data[key]["BMSS Style Label"].encode())
                bmsm_file.write(b"\x00\x00\x00")
                bmsm_file.write(bmsm_data[key]["Message"].encode("UTF-16"))
                bmsm_file.write(b"\x00\x00")
                try:
                    next_item = next_key(bmsm_data, key)
                except StopIteration:
                    break
                for unknown in sorted(bmsm_data[next_item]["Unknowns"], key=len):
                    if unknown != []:
                        bmsm_file.write(
                            unknown.encode() + b"\x00"
                            if len(unknown) != 1
                            else unknown.encode() + b"\x00\x00\x00"
                        )

        print(f"Done writing {self.header.string_count} entries")


# Command line parsing
in_file = argv[1]
out_file = argv[2]

if in_file.endswith("bmsm"):
    file = bmsm(in_file)
    file.to_json(out_file)
elif in_file.endswith("json"):
    file = bmsm(out_file)
    file.from_json(in_file)
