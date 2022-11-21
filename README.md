# PBF -> PNG converter

This tool is for converting Mapbox vector tiles stored in .mbtiles database into .PNG files stored in filesystem

Each .PBF layer is rendered as separate raster layer

## Usage

`mbt = MBTiles("path_to_mbtiles_file")`

`mbt.export("path_to_folder_where_create_raster_tile_layers")`