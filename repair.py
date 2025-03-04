from PIL import Image
import os

def convert_32_to_24(image_path):
    # 打开图片
    img = Image.open(image_path)
    
    # 检查图片的模式，如果是 RGBA（32 位），则转换为 RGB（24 位）
    if img.mode == 'RGBA':
        img = img.convert('RGB')
        # 重新保存图片
        img.save(image_path)
    else:
        img.close()
    

def process_folder(folder_path):
    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 检查文件扩展名，确保处理的是图片文件
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                convert_32_to_24(file_path)

# 示例用法
input_image_path = 'D:/BAAH/DATA/assets_cn/POPUP/POPUP_TASK_INFO.png'
convert_32_to_24(input_image_path)
#folder_path = 'D:/BAAH/DATA/assets/PAGE'
#process_folder(folder_path)