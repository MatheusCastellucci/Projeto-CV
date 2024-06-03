
import cv2
import matplotlib.pyplot as plt
import easyocr
import numpy as np
from PIL import Image

def identificar_texto(image_path, reader): # Função para identificar texto na imagem
    # Carregar a imagem
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Aplicar OCR na imagem para detectar texto
    #reader = easyocr.Reader(['en'])  # Adicionar idiomas conforme necessário
    result = reader.readtext(image_rgb)
    
    # Verificar se há texto
    if result:
        return True


def verificar_cor_azul(image, threshold=0.55, region_fraction=0.3):# Função para verificar a presença de uma cor azul significativa na região inferior da imagem
    # Converter a imagem para o espaço de cores HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Definir o intervalo para a cor azul
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    # Criar uma máscara para a cor azul
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Considerar apenas a região inferior da imagem
    height = mask.shape[0]
    region_height = int(height * region_fraction)
    mask_region = mask[height - region_height:, :]
    
    # Calcular a proporção de pixels azuis na região inferior
    blue_ratio = np.sum(mask_region > 0) / mask_region.size
    return blue_ratio > threshold


def identificar_combate(image_path,reader):# Função para identificar combate na imagem
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    azul_presente = verificar_cor_azul(image)
    
    result = reader.readtext(image_rgb)
    
    detected_texts = []
    if len(result) > 0:
        last_bbox = None
        combined_text = ""
        max_x_distance = 25  # Ajuste conforme necessário
        max_y_distance = 10  # Ajuste conforme necessário
        
        for (bbox, text, prob) in result:
            if last_bbox is not None:
                # Verifica a proximidade dos bounding boxes
                x_distance = bbox[0][0] - last_bbox[2][0]
                y_distance = abs(bbox[0][1] - last_bbox[0][1])
                
                if x_distance < max_x_distance and y_distance < max_y_distance:
                    combined_text += " " + text
                else:
                    detected_texts.append(combined_text)
                    combined_text = text
            else:
                combined_text = text
            
            last_bbox = bbox
        
        # Adiciona o último texto combinado
        if combined_text:
            detected_texts.append(combined_text)
        
    # Combinar os resultados para determinar se é uma cena de combate
    if len(detected_texts) > 0 and azul_presente:
        return True,detected_texts
    else:
        return False,[]
    
def options_cutscene(image_path,reader, offset_x=0, offset_y=0, width=150, height=90):
    # Load the images
    image = cv2.imread(image_path)
    template_path = 'FFVI\\Dialog\\pointer.jpg'
    template = cv2.imread(template_path, 0)
    
    # Template matching to find the arrow
    res = cv2.matchTemplate(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # Coordinates of the matched area
    top_left = max_loc
    h, w = template.shape
    bottom_right = (top_left[0] + w, top_left[1] + h)
    
    # Define the cropping area based on the arrow coordinates
    crop_top_left = (top_left[0] + offset_x, top_left[1] + offset_y)
    crop_bottom_right = (crop_top_left[0] + width, crop_top_left[1] + height)
    
    # Crop the options area
    cropped_options = image[crop_top_left[1]:crop_bottom_right[1], crop_top_left[0]:crop_bottom_right[0]]
    
    # Apply OCR on the cropped image
    #reader = easyocr.Reader(['pt'])
    result = reader.readtext(cropped_options)
    
    # Extract the text from the result
    extracted_text = [text for (bbox, text, prob) in result]
    
    return extracted_text
