import gzip
import mapbox_vector_tile as mvt
import os
import sqlite3
import time

from PIL import Image, ImageDraw, ImageOps
from shapely.geometry import shape
from dotenv import load_dotenv


class MBTiles:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def export(self, out_dir):
        cur = self.conn.cursor()
        sql = 'SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles'

        for row in cur.execute(sql):
            z = int(row[0])
            x = int(row[1])
            y = int(row[2])
            tile = bytes(row[3])
            geojson = mvt.decode(gzip.decompress(tile))

            tr = TileRasterizer(z, x, y, geojson)
            tr.write_layers_png(out_dir)


class TileRasterizer:
    def __init__(self, z, x, y, geojson):
        self.z = z
        self.x = x
        self.y = y
        self.geojson = geojson
        self.timer = {}

    def write_layers_png(self, out_dir):
        for key in self.geojson:
            self.write_layer_png(key, out_dir)

    def write_layer_png(self, layer_name, out_dir):

        t1 = time.time_ns()/1000000000

        layer = self.geojson[layer_name]["features"]
        extent = self.geojson[layer_name]["extent"]
        img = Image.new("RGBA", (extent, extent), "#00000000")
        img_draw = ImageDraw.Draw(img)
        self.plot_layer(img_draw, layer)

        t2 = time.time_ns()/1000000000

        img = img.resize((256, 256), resample=0)
        img = ImageOps.flip(img)
        z2 = int(self.z)
        y2 = pow(2, int(z2)) - int(self.y) - 1

        full_path = os.path.join(
            out_dir,
            f"tiles-{layer_name}",
            str(self.z),
            str(self.x)
        )

        os.makedirs(full_path, exist_ok=True)

        img.save(os.path.join(full_path, f"{y2}.png"))

        t3 = time.time_ns()/1000000000

        self.timer["render"] = t2 - t1
        self.timer["resize"] = t3 - t2

    def plot_layer(self, img, layer):

        for g in layer:

            if g["geometry"]["type"] == "Polygon":
                coord = g["geometry"]["coordinates"]
                ring = coord[0]
                img = self.plot_ring(img, ring, g["properties"])

            if g["geometry"]["type"] == "MultiPolygon":

                ogs = [x.buffer(0) for x in shape(g["geometry"]).buffer(0).geoms]

                for og in ogs:
                    tring = []
                    for cc in og.exterior.coords:
                        tring.append(cc)

                    img = self.plot_tring(img, tring, g["properties"])

        return img

    def plot_ring(self, img, ring, prop):

        tring = []
        for c in ring:
            tring.append((c[0], c[1]))

        return self.plot_tring(img, tring, prop)

    def plot_tring(self, img, tring, prop):

        style = self.polygon_style()

        if "fill" in style:
            img.polygon(tring, fill=style["fill"])

        return img

    @staticmethod
    def polygon_style(prop):
        style = {}
        if prop["s"] == "l":
            style["fill"] = "#86beff80"
        if prop["s"] == "m":
            style["fill"] = "#527fff80"
        if prop["s"] == "s":
            style["fill"] = "#2300ff80"
        return style


load_dotenv()
mbt = MBTiles(os.getenv("MBTILE_SOURCE"))
mbt.export(os.getenv("OUT_DIR"))
