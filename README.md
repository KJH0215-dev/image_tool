🎨 이미지 필터 앱 (Gradio + OpenCV + NumPy)
OpenCV와 NumPy로 구현한 이미지 필터를 Gradio 웹 인터페이스로 제공하는 프로젝트입니다.
Google Colab에서 즉시 실행할 수 있도록 노트북 파일 하나로 구성했습니다.
---
📌 프로젝트 개요
게임·영상 산업에서 사용되는 이미지 후처리 효과를 직접 구현해보는 것을 목표로 합니다.
포토샵의 색조 보정, 게임의 셀 셰이딩, 영화의 컬러 그레이딩처럼 일상에서 접하는 시각 효과들이
실제로는 어떤 수학적 연산으로 만들어지는지 코드로 풀어냈습니다.
만든 이유
컴퓨터 그래픽스 / 이미지 처리의 기초 개념을 손으로 익히기 위해
테크니컬 아티스트(TA)의 작업 영역인 셰이더·후처리 효과의 원리 이해
별도 설치 없이 브라우저에서 바로 체험 가능한 데모를 만들기 위해
---
✨ 주요 기능
카테고리	필터	설명
기본 보정	밝기 / 대비 / 채도 / 색조	선형 변환 + HSV 색공간 변환
컬러 그레이딩	RGB 채널 게인	채널별 가중치 조정 (영화 톤 보정 느낌)
블러	Gaussian / Median / Bilateral / Box	4가지 블러 알고리즘
샤프닝	언샤프 마스크	원본과 블러의 차이를 이용한 경계 강조
엣지 검출	Canny / Sobel / Laplacian	3가지 엣지 검출 방법
스타일	흑백 / 세피아 / 반전 / 카툰 / 연필 스케치 / 유화	다양한 회화·만화 스타일
픽셀화	모자이크	다운샘플 후 nearest 업샘플
---
🛠 기술 스택
Python 3.10+
OpenCV (`opencv-python`) — 이미지 처리 핵심 라이브러리
NumPy — 픽셀 배열 연산
Gradio — 웹 UI (서버 코드 없이 브라우저 인터페이스 자동 생성)
Google Colab — 실행 환경 (별도 환경 구축 불필요)
---
🚀 실행 방법
방법 1. Google Colab (권장)
Google Colab 접속
`파일 → 노트북 업로드`에서 `image_filter_colab.ipynb` 업로드
위에서부터 셀을 순서대로 실행 (`Shift + Enter`)
마지막 셀 실행 시 출력되는 Gradio 링크 클릭
로컬 링크: `http://127.0.0.1:7860`
공유 링크: `https://xxxxx.gradio.live` (72시간 유효)
방법 2. 로컬 실행
```bash
pip install gradio opencv-python numpy
jupyter notebook image_filter_colab.ipynb
```
---
📂 파일 구조
```
.
├── image_filter_colab.ipynb   # 메인 노트북 (모든 코드 포함)
└── README.md                  # 본 문서
```
---
🔍 핵심 함수 설명
`adjust_basic(image, brightness, contrast, saturation, hue)`
픽셀에 선형 변환 (output = α·input + β) 을 적용해 밝기·대비를 조정하고,
HSV 색공간으로 변환해 채도·색조를 조정합니다.
밝기·대비: RGB 픽셀 값에 직접 곱·합 연산
채도·색조: HSV로 변환 → S, H 채널만 조정 → 다시 RGB로 변환
왜 HSV?: RGB에서 채도만 바꾸려면 3채널을 모두 계산해야 하지만, HSV는 S 채널 하나만 곱하면 됨
`apply_blur(image, blur_type, ksize)`
컨볼루션(convolution) 기반의 블러 처리. 작은 행렬(커널)을 이미지 위에서 슬라이딩하며 가중평균을 계산합니다.
Gaussian: 종 모양 가중치 → 자연스러운 흐림
Median: 픽셀의 중앙값 → 점 노이즈(소금-후추) 제거에 강함
Bilateral: 경계는 살리고 색만 평탄화 → 카툰 필터의 핵심
Box: 균일 가중치 → 빠르지만 부자연스러움
`apply_sharpen(image, amount)`
언샤프 마스크(Unsharp Mask) 기법. 원본에서 블러된 버전을 빼면 "고주파 성분(경계)"만 남는다는 원리:
```
sharpened = original + amount × (original − blurred)
```
`apply_edge(image, method, threshold1, threshold2)`
Canny 알고리즘의 4단계:
Gaussian Blur: 노이즈 제거
Sobel Filter: x/y 방향 그래디언트 계산
Non-maximum Suppression: 엣지를 1픽셀 두께로 얇게
이중 임계값(Hysteresis): 강한 엣지에 연결된 약한 엣지만 살림
`apply_style(image, style)` — 카툰 필터
셀 셰이딩(Cel Shading) 의 원리와 동일한 3단계 합성:
Bilateral Filter × 2회 → 색 영역을 단순화 (경계는 유지)
Adaptive Threshold → 윤곽선만 흑백으로 추출
bitwise_and → 단순화된 색 + 윤곽선 합성
`apply_pixelate(image, pixel_size)`
이미지를 작게 축소했다가 Nearest Neighbor 보간으로 다시 키워서 픽셀 단위의 모자이크 효과를 만듭니다.
---
🎮 TA(테크니컬 아티스트) 관점의 응용
본 프로젝트의 필터	게임·영상에서의 실제 사용처
카툰 필터	셀 셰이딩 셰이더 (젤다 야숨, 보더랜드, 페르소나 5)
엣지 검출	외곽선 강조 포스트 프로세스 (Outline Shader)
RGB 채널 / 세피아	컬러 그레이딩 LUT (영화 톤 보정)
픽셀화	레트로 게임 효과, 검열 처리
블러 (Gaussian)	Bloom, Depth of Field, Motion Blur 의 기반
언샤프 마스크	UI/텍스트 가독성 향상, 디테일 강조
---
📚 참고 자료
OpenCV 공식 문서
Gradio 공식 문서
Canny Edge Detection (Wikipedia)
Bilateral Filter (논문 원문)
---
📝 라이선스
학습·발표 목적의 프로젝트입니다.
