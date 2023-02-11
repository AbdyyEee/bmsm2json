# bmsm2json
A script that converts Streetpass Mii Plaza's message files (`bmsm`) to json and back.

See `text_sample.json` for the syntax of this file.

# Usage

## Exporting
```
bmsm [in_file.bmsm] [out_file.json]
```

## Importing 
```
For importing to an existing bmsm file:

bmsm [in_file.json] [existing_file.bmsm]

For importing to a new not created bmsm file

bmsm [in_file.json] [new_bmsm_filename.bmsm]
```

