#!/bin/bash
set -o errexit -o nounset -o pipefail
cd "$(dirname "$0")/.."

glyphs_file=${FIRACODE_GLYPHS_FILE:-"FiraCode.glyphs"}

code_blocks=()

for feat in "$@"; do

	file="features/${feat}.fea"
	if [ ! -f "${file}" ]; then
		echo "Error: No file for feature ${feat} found!" >&2
		exit 1
	fi

	# don't grab the "lookup" surroundings or comments or whitespace lines
	code="$(grep -v '^[[:space:]]*lookup\|^[[:space:]]*}\|^[[:space:]]*#\|^[[:space:]]*$' "${file}")" \
		|| { echo "Error: No code for feature ${feat} found!" >&2; exit 1; }

	code_blocks+=("$(tr '\n' ' ' <<< "${code}")")
done

# Keep baked substitutions out of `calt`. Applications commonly disable that
# feature with their "Enable ligatures" setting, which used to disable the
# supposedly baked-in variants as well. `rclt` (required contextual alternates)
# is enabled by default independently of optional ligature settings.
#
# Insert the feature after `calt`, rather than before it, so substitutions that
# target glyphs produced by Fira Code's contextual pipeline can still run.
calt_tag_line=$(sed -n "/tag = calt;/=" "${glyphs_file}")
tmp_file=$(mktemp)

{
	head -n "$((calt_tag_line + 1))" "${glyphs_file}"
	printf '{\ncode = "%s";\ntag = rclt;\n},\n' "${code_blocks[*]}"
	tail -n "+$((calt_tag_line + 2))" "${glyphs_file}"
} > "${tmp_file}"

mv "${tmp_file}" "${glyphs_file}"
