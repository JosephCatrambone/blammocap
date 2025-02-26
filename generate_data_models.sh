#! /usr/bin/env datamodel-codegen - input datamodels.py - output datamodels.ts - target typescript
pip install datamodel-code-generator
datamodel-codegen  --input protocol.json --input-file-type jsonschema --output datamodels.py
datamodel-codegen  --input protocol.json --input-file-type jsonschema --output datamodels.ts