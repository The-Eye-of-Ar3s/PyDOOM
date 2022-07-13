""" Module for the PyDOOM WAD Class"""

import json

import imageio
import numpy as np

from lib.exceptions import UnrecognizedWADFormat


class WAD:
    """ Class for the DOOM WAD File
    """
    def __init__(self, path):
        print(f"LOADING {path}")
        with open(path, "rb") as raw_wad:
            self.raw = raw_wad.read()
        self.wad = {}
        self.data = {}

        # LOAD HEADER
        wad_type = "".join([chr(i) for i in self.raw[0:4]])
        if wad_type not in ["IWAD", "PWAD"]:
            raise UnrecognizedWADFormat
        numlump = int.from_bytes(self.raw[4:8], "little", signed=True)
        directory_pointer = int.from_bytes(self.raw[8:12], "little", signed=True)

        self.wad["header"] = {
            "wad_type": wad_type,
            "numlump": numlump,
            "directory_entry_pointer": directory_pointer
        }


        # LOAD DIRECTORY

        tempdir = {}
        ind = 0
        for i in range(numlump):
            directory_lump_pointer = directory_pointer+i*16
            lump_data_pointer = int.from_bytes(
                self.raw[directory_lump_pointer: directory_lump_pointer+4],
                "little",
                signed=True)
            lump_data_size = int.from_bytes(
                self.raw[directory_lump_pointer+4: directory_lump_pointer+8],
                "little",
                signed=True)
            lump_data_name = str(
                [self.raw[directory_lump_pointer+8: directory_lump_pointer+16]]
            ).replace("\\x00", "")[3:-2]
            tempdir[ind] = {
                "name":lump_data_name,
                "pointer": lump_data_pointer,
                "size": lump_data_size
                }
            ind += 1
        self.wad["directory"] = tempdir

        del numlump
        del directory_pointer
        del lump_data_name
        del lump_data_pointer
        del lump_data_size
        del tempdir

        # LOAD LUMP DATA

        tempdir = {}

        for lump_index in self.wad["directory"]:
            lump_info = self.wad["directory"][lump_index]
            tempdir[lump_index] = {
                "name": self.wad["directory"][lump_index]["name"],
                "data":
                    self.raw[
                    lump_info["pointer"]: lump_info["pointer"] + lump_info["size"]
                    ]
                }

        self.wad["lump_data"] = tempdir

        del tempdir

        self.read_playpal()
        self.read_colormap()

        # Write PLAYPAL Palettes to images
        #for index, value in enumerate(self.data["playpal"]):
        #    imageio.imwrite(f"img/playpal_{index+1}.png",np.array(value).reshape((16,16,3)))

        # Write COLORMAP Maps to images
        #for index, value in enumerate(self.data["colormap"]):
        #    imageio.imwrite(f"img/colormap_{index}.png",np.array(value).reshape((16,16,3)))

        # patch_to_nparray test for EXIT1 patchlump
        #imageio.imwrite("Exit1.png",self.patch_to_nparray(self.wad["lump_data"][1824]["data"]))

        # flat_to_nparray test for TLITE6_1 flatlump
        #imageio.imwrite("Flat.png",self.flat_to_nparray(self.wad["lump_data"][2101]["data"]))
        
        #if wad_type == "IWAD":
        #    self.iwad_handler()
        #elif wad_type == "PWAD":
        #    self.pwad_handler()

        # SAVE WAD AS JSON

        with open(f"{path}.json", "wt", encoding="utf-8") as out:
            tempdir = self.wad
            for key in tempdir["lump_data"].keys():
                tempdir["lump_data"][key]["data"] = tempdir["lump_data"][key]["data"].hex()
                # Convert Binary Data to hex format so i can dump it in a json file
            out.write(json.dumps(tempdir))

    def read_playpal(self):
        """read_playpal
        Reads a binary PLAYPAL Lump and turns it into an array of np array images (PIL)
        """
        for i in self.wad["lump_data"]:
            if self.wad["lump_data"][i]["name"] == "PLAYPAL":
                playpal_raw = self.wad["lump_data"][i]["data"]
                break
        playpal_ints = [np.uint8(i) for i in playpal_raw]
        playpal_grouped = [playpal_ints[i:i+3] for i in range(0, len(playpal_ints), 3)]
        pallets = [playpal_grouped[i:i+256] for i in range(0, len(playpal_grouped), 256)]
        self.data["playpal"] = pallets

    def read_colormap(self):
        """read_colormap
        Reads a binary COLORMAP Lump and turns it into an array of np array images
        """
        for i in self.wad["lump_data"]:
            if self.wad["lump_data"][i]["name"] == "COLORMAP":
                colormap_raw = self.wad["lump_data"][i]["data"]
                break
        colormap_ungrouped = [self.data["playpal"][0][i] for i in colormap_raw]
        self.data["colormap"] = [
            colormap_ungrouped[i:i+256] for i in range(0, len(colormap_ungrouped), 256)
            ]


    #@staticmethod
    #def byte_to_rgb(bt):
    #    color_bits = format(bt, '08b')
    #    red = (int(color_bits[0:3], 2))*32
    #    green = (int(color_bits[3:6], 2))*32
    #    blue = (int(color_bits[6:8], 2))*64
    #    return (red, green, blue)


    def patch_to_nparray(self, patchfile):
        """patch_to_nparray
            vert a DOOM Patchfile (DOOM Image format) into a python readable 2D_nparray

        Parameters
        ----------
        patchfile : bytestring
            Patchfile WAD Lump
        colormap : array[int]
            Currently active colormap

        Returns
        -------
        arr[arr[tuple()]]
            nparray image
        """
        #print(patchfile[0:2])
        #print(type(patchfile[0:2]))
        i = 0
        #print(patchfile[8+i*4:8+i*4+4])
        #print(type(patchfile[8+i*4:8+i*4+4]))

        width = int.from_bytes(patchfile[0:2], "little", signed=False)
        # Image Width in px
        #height = int.from_bytes(patchfile[2:4], "little", signed=False)
        # Image Height in px
        image = []
        # Output Image
        #leftoffset = int.from_bytes(patchfile[0:2], "little", signed=True)
        # ??
        #topoffset = int.from_bytes(patchfile[2:4], "little", signed=True)
        # ??
        # TODO: understand & utilize offsets
        columnofs = [
            int.from_bytes(patchfile[8+i*4:8+i*4+4], "little", signed=False) for i in range(width)
            ]
        ind = 0
        for column_pointer in columnofs:
            topdelta = int.from_bytes(
                patchfile[column_pointer: column_pointer+1], "little", signed=False
                )
            if topdelta == 255:
                break
            length = int.from_bytes(
                patchfile[column_pointer+1: column_pointer+2], "little", signed=False
                )
            data = [
                self.data["colormap"][0][i]
                for i in patchfile[column_pointer+3: column_pointer+length+3]
                ]
            image.append(data)
            ind += 1

        # Fix orientation of image
        rimg = []
        for row_num in range(len(image[0])):
            line = []
            for column in image:
                line.append(column[row_num])
            rimg.append(line)
        return np.array(rimg)

    def flat_to_nparray(self, flatfile):
        """flat_to_nparray
        converts a flat lump to a np array image

        Parameters
        ----------
        flatfile : 4096 byte lump
            lump containing colormap indicies for a flat sprite

        Returns
        -------
        np array
            np array image
        """
        flatints = [i for i in flatfile]
        i = 0
        image = []
        for _ in range(64):
            l = []
            for __ in range(64):
                l.append(self.data["colormap"][0][flatints[i]])
                i += 1
            image.append(l)

        return np.array(image)
