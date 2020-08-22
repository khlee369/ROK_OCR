# ROK_OCR
managing for member's power

OpenCV 와 Tesseract OCR 엔진을 이용하여
녹스 앱 플레이어 화면을 캡쳐 후 연맹원 전투력을 엑셀로 변환시켜 줍니다.

OpenCV로 image search를 하여 원하는 이미지를 클릭하는식으로 구현되어 있습니다.

이 프로그램은 크게 3가지 스텝으로 이루어져 있습니다.

1. 연맹원 프로필 캡쳐
2. 연맹원 프로필 OCR(e.g. ID, 전투력)
3. 엑셀로 변환 후 저장

## MUST CHECK
- Nox App Player : 6.6.0.9
    - 연맹원 프로필을 캡쳐할때 녹스의 캡쳐기능을 사용합니다. 녹스의 버전에 따라 캡쳐하기 icon의 위치와 형태가 다르기 때문에 버전이 다르면 캡쳐를 하지 못하는 경우가 발생합니다. 다른 버전의 녹스를 사용하신다면 해당 부분의 코드를 바꾸셔서 사용하셔야 합니다.

- Nox Resolution
    - 녹스의 해상도는 태블릿, 1280x720으로 해주시기 바랍니다. image search가 불필요한 부분에 대해서는 pixel wise fixed point를 사용하기 때문에 해상도가 달라지면 제대로 작동하지 않습니다. 해당부분은 개발 예정 이었으나 1 pixel 차이로 OCR이 실패하거나 클릭미스가 나는 경우가 있기 때문에 추후에 다시 검토할 예정입니다.


## Recommended Version
- python : 3.6.10
- OpenCV : 3.4.2
- mss : 6.0.0
