# bmsm2json
A script that converts Streetpass Mii Plaza's message files (`bmsm`) to json and back.

See `text_sample.json` for the syntax of this file.

# Usage

## Exporting
```
bmsm -export [in_file.bmsm] [out_file.json]
```

## Importing 
```
bmsm -import [in_file.json] [existing_file.bmsm]
```

## Creating New File
```
bmsm -newfile [new_bmsm_filename.bmsm]
```


