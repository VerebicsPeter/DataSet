#!/bin/bash

resource_dir="$HOME/Documents/DataSet/resources/scripts"

function refactor {
    if [ "$1" != "isort" ] && [ "$1" != "autopep" ] && [ "$1" != "modernize" ]; then
        [ -z "$1" ] && 
        echo -e "Can't refactor: no method." || 
        echo -e "Can't refactor: no method named $1."
        return
    fi
    # Iterate over Python scripts in the directory
    for script in "$resource_dir"/*.py; do
        # Get the base name of the script (without the path or extension)
        base_name=$(basename "$script" .py)

        if [[ $base_name == *"isort"* ]]; then
            echo -e ">> Skipping already isorted file: $script\n"
            continue
        fi

        if [[ $base_name == *"autopep"* ]]; then
            echo -e ">> Skipping already autopepped file: $script\n"
            continue
        fi

        if [[ $base_name == *"modernize"* ]]; then
            echo -e ">> Skipping already modernized file: $script\n"
            continue
        fi

        # Create copy of the script
        cp "$script" "$resource_dir/$base_name.$1.py"

        # Run isort on the copy of the script
        if [[ $1 == "isort" ]]; then
            isort $resource_dir/$base_name.$1.py
        fi
        # Run autopep on the copy of the script
        if [[ $1 == "autopep" ]]; then
            autopep8 --in-place --aggressive --aggressive $resource_dir/$base_name.$1.py
        fi
        # Run modernize on the copy of the script
        if [[ $1 == "modernize" ]]; then
            modernize --no-six --nobackups -w "$resource_dir/$base_name.$1.py"
        fi

        # Check if there were any changes made to the copy
        if cmp -s "$script" "$resource_dir/$base_name.$1.py";
        then
            echo -e ">> No changes needed for $script\n"
            # Remove the copy if no changes were made
            rm "$resource_dir/$base_name.$1.py"
        else
            echo -e ">> Changes applied to $script\n"
        fi
    done
}

refactor $1