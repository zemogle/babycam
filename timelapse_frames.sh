wget -q http://localhost:8000/latest.jpg
convert latest.jpg -background '#0008' -fill white \
    -pointsize 36 -font arial caption:$(date +%Y:%m:%dT%H:%M)  \
-gravity northwest -compose dstout -composite -alpha on latest.jpg
mv latest.jpg /home/pi/images/image$(date +%Y%m%d%H%M).jpg
