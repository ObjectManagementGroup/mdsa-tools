#####
# converttomd.sh
# This script is to be used ONCE at the beginning of your authoring project.
#
#               ONCE. 
#
# We cannot stress this enough. Running it later will *overwrite* your Markdown files 
# if there are still any of the core tex files in the directory.

mkdir -p ./temptex
for file in ./[0-9A]*.tex; do
    filesize=$(du -k "${file}" | cut -f1)
    target="${file%.tex}.md"
    if ((filesize > 0)) 
    then
        echo "Converting ${file} to ${target}"
        # pandoc ${file} -f latex+raw_tex -t markdown -o ${target}
    else
        echo "${file} is zero length, touching ${target}"
        # touch ${target}
    fi
    # mv ${file} temptex/${file}
done
