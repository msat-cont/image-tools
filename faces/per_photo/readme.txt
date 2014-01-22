
The 'detect.py' script tries to detect faces in a given picture,
and if it finds several faces in the given picture, it compares them.

Face detection works via OpenCV.
https://github.com/Itseez/opencv

Face recognition works via Mahots.
https://github.com/luispedro/mahotas

It seems that under the current script setting, and with used testing images,
distance up to 0.10 is for the same faces, and up to 0.15 for similar faces.
Random faces have distance around 0.20, and cca 0.25 is for quite dissimilar
faces. Your mileage may vary.

Notice that the script has conservative setting for face detection, i.e. it
tries to avoid false positives, and thus it does not detect quite a few faces.


