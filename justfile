default:
    just --list

generate-schema source destination:
    uv run datamodel-codegen \
        --formatters ruff-format \
        --input-file-type jsonschema \
        --output {{destination}} \
        --output-model-type pydantic_v2.BaseModel \
        --{{if source =~ 'https://+*' { "url" } else { "input" }}} {{source}} \
        --base-class homelab_pydantic.HomelabBaseModel \
        --disable-future-imports \
        --enum-field-as-literal none \
        --field-constraints \
        --set-default-enum-member \
        --use-enum-values-in-discriminator \
        --use-non-positive-negative-number-constrained-types \
        --use-specialized-enum \
        --use-standard-collections \
        --use-union-operator \
        --use-unique-items-as-set \
        --capitalise-enum-members \
        --snake-case-field \
        --naming-strategy full-path \
        --disable-timestamp \
        --target-pydantic-version 2.11 \
        --target-python-version 3.14
