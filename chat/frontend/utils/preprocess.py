import re
import os

FLAGS = {
    "TESTING": True,
    "DEBUG": False,
}

IFDEF_PATTERN = re.compile(r"#ifdef (\w+)")
IFNDEF_PATTERN = re.compile(r"#ifndef (\w+)")
INCLUDE_PATTERN = re.compile(r'#include "([\w\./]+)"')


# TODO: parse conditions
# TODO: variables
def preprocess_file(input_path, output_path):
    with open(input_path, "r") as file:
        lines = file.readlines()

    output = []
    i = 0
    level = 0
    skip = False
    skip_from_level = 0

    while i < len(lines):
        line = lines[i]
        if lines[i].strip().startswith("#endif"):
            level -= 1
            if level < 0:
                raise ValueError("Mismatched #endif directive")
            skip = level < skip_from_level
            i += 1
            continue
        ifdef_match = IFDEF_PATTERN.match(line.strip())
        ifndef_match = IFNDEF_PATTERN.match(line.strip())

        if skip:
            i += 1
            if ifdef_match or ifndef_match:
                level += 1
            continue

        # #ifdef
        if ifdef_match:
            condition = ifdef_match.group(1)
            if condition in FLAGS and FLAGS[condition]:
                pass
            else:
                skip = True
                skip_from_level = level
            level += 1
            i += 1
            continue

        # #ifndef
        if ifndef_match:
            condition = ifndef_match.group(1)
            if condition not in FLAGS or not FLAGS[condition]:
                pass
            else:
                skip = True
                skip_from_level = level
            level += 1
            i += 1
            continue

        # #include
        include_match = INCLUDE_PATTERN.match(line.strip())
        if include_match:
            included_file = include_match.group(1)
            included_path = os.path.join(os.path.dirname(input_path), included_file)
            if not os.path.exists(included_path):
                raise FileNotFoundError(f"Included file not found: {included_path}")
            output.extend(preprocess_file(included_path, output_path))
            i += 1
            continue

        output.append(line)
        i += 1

    with open(output_path, "w") as file:
        file.writelines(output)

    return output


input_file = os.path.join("neon/src", "index.html")
output_file = os.path.join("neon/dist", "index.html")
preprocess_file(input_file, output_file)

print(f"Preprocessed page saved to {output_file}")
