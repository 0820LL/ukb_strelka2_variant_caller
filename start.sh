#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "The script need exactly 1 argument: config.json"
    echo "/.../$0 /.../config.json"
    exit
fi

config_file="$1"
analysis_dir=$(dirname "$config_file")
script_path="$(dirname "$(realpath "$0")")"
sendMessage=$(jq ".jms" "$script_path"/../../config/configuration.json | sed 's/\"//g')

cd "$analysis_dir" || exit
python3 "$script_path"/ukb_strelka2_variant_caller_wrapper.py \
    --cfp "$config_file" \
    --ukb_strelka2_variant_caller_path "$script_path"/workflow/main.nf \
    --send_message_script "$sendMessage"
