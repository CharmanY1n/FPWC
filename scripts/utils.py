import base64
import cv2 
import pyshine as ps
import os
from colorama import Fore, Style 
from PIL import Image 

def print_with_color(text: str, color=""): 
    if color == "red":
        print(Fore.RED + text)
    elif color == "green":
        print(Fore.GREEN + text)
    elif color == "yellow":
        print(Fore.YELLOW + text)
    elif color == "blue":
        print(Fore.BLUE + text)
    elif color == "magenta":
        print(Fore.MAGENTA + text)
    elif color == "cyan":
        print(Fore.CYAN + text)
    elif color == "white":
        print(Fore.WHITE + text)
    elif color == "black":
        print(Fore.BLACK + text)
    else:
        print(text)
    print(Style.RESET_ALL) 




def draw_bbox_multi(img_path, output_path, elem_list, record_mode=False, dark_mode=False):

    imgcv = cv2.imread(img_path) 
    count = 1 
    for elem in elem_list:
        try:

            top_left = elem.bbox[0]
            bottom_right = elem.bbox[1]
            left, top = top_left[0], top_left[1]
            right, bottom = bottom_right[0], bottom_right[1] 

            label = str(count)
            if record_mode: 
                if elem.attrib == "clickable":
                    color = (250, 0, 0) 
                elif elem.attrib == "focusable":
                    color = (0, 0, 250) 
                else:
                    color = (0, 250, 0) 
                

                imgcv = ps.putBText(imgcv, label, text_offset_x=(left + right) // 2 + 10, text_offset_y=(top + bottom) // 2 + 10,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=color,
                                    text_RGB=(255, 250, 250), alpha=0.5)
            else:
                text_color = (10, 10, 10) if dark_mode else (255, 250, 250) 
                bg_color = (255, 250, 250) if dark_mode else (10, 10, 10)
                imgcv = ps.putBText(imgcv, label, text_offset_x=(left + right) // 2 + 10, text_offset_y=(top + bottom) // 2 + 10,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=bg_color,
                                    text_RGB=text_color, alpha=0.5)
        except Exception as e:
            print_with_color(f"ERROR: An exception occurs while labeling the image\n{e}", "red")
        count += 1
    cv2.imwrite(output_path, imgcv) 
    
    return count-1 



def draw_grid(img_path, output_path):

    def get_unit_len(n):
        for i in range(1, n + 1):
            if n % i == 0 and 120 <= i <= 180:
                return i
        return -1

    image = cv2.imread(img_path) 

    height, width, _ = image.shape

    color = (0, 0, 255) 


    unit_height = get_unit_len(height)
    if unit_height < 0:
        unit_height = 120
    unit_width = get_unit_len(width)
    if unit_width < 0:
        unit_width = 120


    thick = int(unit_width // 50)


    rows = height // unit_height
    cols = width // unit_width


    for i in range(rows):
        for j in range(cols):
            label = i * cols + j + 1 
            left = int(j * unit_width)
            top = int(i * unit_height)
            right = int((j + 1) * unit_width)
            bottom = int((i + 1) * unit_height)
            
            cv2.rectangle(image, (left, top), (right, bottom), color, thick // 2)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05) + 3, top + int(unit_height * 0.3) + 3), 0,
                        int(0.01 * unit_width), (0, 0, 0), int(thick *0.8))
            
            cv2.putText(image, str(label), (left + int(unit_width * 0.05), top + int(unit_height * 0.3)), 0,
                        int(0.01 * unit_width), color, int(thick *0.8))
    cv2.imwrite(output_path, image)
    return rows, cols



def encode_image(image_path):
    with open(image_path, "rb") as image_file: 
        return base64.b64encode(image_file.read()).decode('utf-8')




def read_txt_files(directory):
    files = os.listdir(directory)

    result = ''
    for file in files:
        if file.endswith('.txt'):
            filename = os.path.splitext(file)[0]
            with open(os.path.join(directory, file), 'r') as f:
                content = f.read()
            result += f'{filename}\n{content}\n'
    
    return result


def crop_image(image_path, coords, save_path):
    print(coords)
    image = Image.open(image_path)
    center_x = (coords[0] + coords[2]) / 2
    center_y = (coords[1] + coords[3]) / 2
    new_width = (coords[2] - coords[0]) * 1.1
    new_height = (coords[3] - coords[1]) * 1.1
    new_coords = (
        center_x - new_width / 2,
        center_y - new_height / 2,
        center_x + new_width / 2,
        center_y + new_height / 2+20
    )
    cropped_image = image.crop(new_coords)
    cropped_image.save(save_path)
