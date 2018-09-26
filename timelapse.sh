find /home/pi/images/image20*.jpg -type f -cmin -720 -exec cat {} \; | ffmpeg -f image2pipe -framerate 10 -i - -s 696x520 -vcodec libx264  -pix_fmt yuv420p latest.mp4 -y
cp latest.mp4 /home/pi/videos/$(date +%Y%m%d%H%M).mp4
