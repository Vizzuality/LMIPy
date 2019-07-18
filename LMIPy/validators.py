import warnings
import jsonschema
import json

def initialize_validator_warn():
    warnings.formatwarning = custom_formatwarning
    return

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return str(msg) + '\n'

def layer_validator(id_hash, warn_type, params):
    if warn_type == 'layerConfig':
        lc = params.get('layerConfig', None)
        if lc: valid, msg = validate_layer_config(id_hash=id_hash, config=lc)
    
    if not valid:
        return warnings.warn(msg, Warning)
    else:
        return 

def validate_layer_config(id_hash, config):
    # check config against standard schema.
    # See https://stackoverflow.com/questions/48671629/how-to-check-json-format-validation
    # also https://python-jsonschema.readthedocs.io/en/stable/
    # and https://github.com/resource-watch/notebooks/blob/develop/ResourceWatch/Api_definition/layer_definition.ipynb


    carto_schema = {
        "type": "object",
        "properties": {
            "account": {"type": "string"},
            "body": {
                "type": "object",
                "properties": {
                    "maxzoom": {"type": "number"},
                    "minzoom": {"type": "number"},
                    "layers": {
                        "type": "array",
                        "properties": {
                            "type": {"type": "options"},
                            "options": {"type": "object"}
                        }
                    },
                    "vectorLayers": {"type": "array"}
                }
            }
        }
    }   

    # jsonschema.validate(config, carto_schema)

    msg = f"WARN: Bad schema detected in Layer {id_hash}.\n\nConsider updating using `Layer.makeValid`."
    return [False, msg]