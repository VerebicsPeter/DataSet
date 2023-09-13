#!/bin/bash

# Directory containing the Python scripts
resource_dir="/home/peter/Documents/DataSet/resources/scripts"

# Iterate over Python scripts in the directory
for script in "$resource_dir"/*.py;
do
    # Get the base name of the script (without the path or extension)
    base_name=$(basename "$script" .py)

    if [[ $base_name == *"modernize"* ]];
    then
        echo -e ">> Skipping already modernized file: $script\n"
        continue
    fi

    # Create copy of the script
    cp "$script" "$resource_dir/$base_name.modernize.py"

    # Run modernize on the copy of the script
    modernize --no-six --nobackups -w "$resource_dir/$base_name.modernize.py"

    # Check if there were any changes made to the copy
    if cmp -s "$script" "$resource_dir/$base_name.modernize.py";
    then
        echo -e ">> No changes needed for $script\n"
        # Remove the copy if no changes were made
        rm "$resource_dir/$base_name.modernize.py"
    else
        echo -e ">> Changes applied to $script\n"
    fi
done