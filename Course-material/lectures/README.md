## Note for the Teacher
All files must be 100mb or smaller. If your file is larger, you can compress it with ffmpeg (free, cross-platform). Quick, good-quality compression (recommended): 
```bash
ffmpeg -i input.mp4 -vcodec libx264 -preset slow -crf 23 -acodec aac -b:a 100k output.mp4
```
- Lower ``-crf`` : higher quality & bigger file (try 20–23).
