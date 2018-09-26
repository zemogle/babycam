convert latest.jpg -background '#0008' -fill white \
    -pointsize 36 -font arial caption:$(date +%Y:%m:%dT%H:%M)  \
-gravity northwest -compose dstout -composite -alpha on latest.jpg
