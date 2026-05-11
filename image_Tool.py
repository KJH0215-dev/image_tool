import gradio as gr         
import numpy as np           
from PIL import Image, ImageFilter 
import matplotlib.colors as mcolors
presets = {
   
    "기본값":      (1.0, 1.0, 0, False), 
    "따뜻한 느낌": (1.2, 1.5, 0, False), 
    "흑백 스케치": (1.0, 0.0, 0, True),  
    "몽환적":      (0.8, 1.3, 5, False),  
    "선명하게":    (1.3, 1.8, 0, False),  
    "빈티지":      (0.9, 0.6, 1, False),  
}


def process_image(image, brightness, saturation, blur_radius, show_edge):
    """
    이미지에 기본 필터들을 순서대로 적용하는 함수

    [매개변수 설명]
    - image       : 업로드한 원본 이미지 (PIL Image 형식)
    - brightness  : 밝기 배율 (1.0=원본, 2.0=2배 밝게, 0.5=절반 어둡게)
    - saturation  : 채도 배율 (1.0=원본, 0.0=흑백, 2.0=2배 선명하게)
    - blur_radius : 블러 반지름 (0=블러없음, 숫자 클수록 더 흐릿하게)
    - show_edge   : 엣지 감지 여부 (True=윤곽선만 표시, False=일반 이미지)

    [반환값]
    - 필터가 적용된 PIL Image
    """
    if image is None:
        return None
    img_array = np.array(image)
    img_array = np.clip(img_array * brightness, 0, 255).astype(np.uint8)
    img_float = img_array / 255.0
    img_hsv = mcolors.rgb_to_hsv(img_float)
    img_hsv[:, :, 1] = np.clip(img_hsv[:, :, 1] * saturation, 0, 1)
    img_array = (mcolors.hsv_to_rgb(img_hsv) * 255).astype(np.uint8)

    img_pil = Image.fromarray(img_array)

    if blur_radius > 0: 
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    if show_edge:
        img_pil = img_pil.filter(ImageFilter.FIND_EDGES)

    return img_pil 


def color_splash(image, target_color, threshold):
    """
    Color Splash 효과를 적용하는 함수
    선택한 색상과 비슷한 픽셀만 컬러로 남기고, 나머지는 흑백으로 변환

    [동작 원리]
    1. 전체 이미지를 흑백으로 변환
    2. 각 픽셀과 선택한 색상의 차이를 계산
    3. 차이가 threshold보다 작은 픽셀 → 원본 컬러 유지
    4. 차이가 threshold보다 큰 픽셀 → 흑백으로 변환

    [매개변수 설명]
    - image        : 원본 이미지 (PIL Image 형식)
    - target_color : 남길 색상 (hex 코드 문자열, 예: "#FF0000" = 빨강)
    - threshold    : 색상 허용 범위 (0~255, 높을수록 비슷한 색도 컬러로 남김)

    [반환값]
    - Color Splash가 적용된 PIL Image
    """

    if image is None:
        return None

    target_color = target_color.lstrip('#')
    target_rgb = tuple(int(target_color[i:i+2], 16) for i in (0, 2, 4))

    img_array = np.array(image).astype(np.float32)

    gray = (0.299 * img_array[:,:,0] +   
            0.587 * img_array[:,:,1] + 
            0.114 * img_array[:,:,2])    
  
    diff_r = np.abs(img_array[:,:,0] - target_rgb[0])  
    diff_g = np.abs(img_array[:,:,1] - target_rgb[1])
    diff_b = np.abs(img_array[:,:,2] - target_rgb[2])  

    color_diff = (diff_r + diff_g + diff_b) / 3

    color_mask = color_diff < threshold

    result = np.zeros_like(img_array)

    result[color_mask] = img_array[color_mask]

    for channel in range(3): 
        result[:,:,channel][~color_mask] = gray[~color_mask]

    return Image.fromarray(result.astype(np.uint8))


def apply_preset(preset_name):
    """
    프리셋 이름을 받아서 해당 설정값을 반환하는 함수

    [동작 방식]
    딕셔너리에서 키(프리셋 이름)로 값(설정값 튜플)을 조회
    반환된 값이 각 슬라이더/체크박스에 자동으로 적용됨

    [매개변수]
    - preset_name: 선택한 프리셋 이름 (딕셔너리의 키)

    [반환값]
    - 밝기, 채도, 블러, 엣지감지 값 (4개)
    """

    values = presets[preset_name]
    return values[0], values[1], values[2], values[3]

with gr.Blocks(title="필터 툴") as demo:

    gr.Markdown("#이미지 필터 툴")
    gr.Markdown("이미지를 업로드하고 필터를 조절해보세요!")

    with gr.Tabs():
        with gr.Tab("기본 필터"):
            with gr.Row():

                with gr.Column():
                    input_image1 = gr.Image(type="pil", label="이미지 업로드")
                    preset_dropdown = gr.Dropdown(
                        choices=list(presets.keys()), 
                        value="기본값",              
                        label="프리셋 선택 (선택 시 슬라이더 자동 변경)"
                    )
                    brightness_slider = gr.Slider(
                        minimum=0.1, maximum=3.0,
                        value=1.0, label="밝기 (1.0=원본)"
                    )
                    saturation_slider = gr.Slider(
                        minimum=0.0, maximum=3.0,
                        value=1.0, label="채도 (0=흑백, 1.0=원본)"
                    )
                    blur_slider = gr.Slider(
                        minimum=0, maximum=10,
                        value=0, label="블러 강도 (0=없음)"
                    )
                    edge_checkbox = gr.Checkbox(label="엣지 감지")

                    apply_btn1 = gr.Button("필터 적용", variant="primary")

                with gr.Column():
                    output_image1 = gr.Image(label="결과 이미지")

            preset_dropdown.change(
                fn=apply_preset,
                inputs=[preset_dropdown],
                outputs=[brightness_slider, saturation_slider,
                         blur_slider, edge_checkbox]
            )

            apply_btn1.click(
                fn=process_image,
                inputs=[input_image1, brightness_slider,
                        saturation_slider, blur_slider, edge_checkbox],
                outputs=[output_image1]
            )
        with gr.Tab("Color Splash"):
            gr.Markdown("### 원하는 색상만 살리고 나머지는 흑백으로!")
            gr.Markdown("팁: 감지 범위를 낮추면 정확한 색만, 높이면 비슷한 색도 포함됩니다")

            with gr.Row():
                with gr.Column():
                    input_image2 = gr.Image(type="pil", label="이미지 업로드")
                    color_picker = gr.ColorPicker(
                        value="#FF0000",
                        label="남길 색상 선택 (클릭해서 색 고르기)"
                    )
                    threshold_slider = gr.Slider(
                        minimum=10, maximum=150,
                        value=60, step=5,
                        label="색상 감지 범위 (낮을수록 정확, 높을수록 넓게)"
                    )

                    splash_btn = gr.Button("Color Splash 적용", variant="primary")

                with gr.Column():
                    output_image2 = gr.Image(label="결과 이미지")
            splash_btn.click(
                fn=color_splash,
                inputs=[input_image2, color_picker, threshold_slider],
                outputs=[output_image2]
            )

demo.launch()
