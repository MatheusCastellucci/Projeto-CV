import cv2
import os
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pickle

def plot_hsv(hist_h, hist_s, hist_v):
    # Criar a grade de subplots
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Plotar o primeiro gráfico
    axs[0].plot(hist_h)
    axs[0].set_title('H')

    # Plotar o segundo gráfico
    axs[1].plot(hist_s)
    axs[1].set_title('S')

    # Plotar o terceiro gráfico
    axs[2].plot(hist_v)
    axs[2].set_title('V')

    # Ajustar layout para evitar sobreposição de rótulos
    plt.tight_layout()

    # Mostrar os gráficos
    plt.show()

def plot_diff(hist):
    # Calcular a primeira derivada do histograma
    first_derivative = np.diff(hist.squeeze())
    first_derivative = np.convolve(first_derivative.squeeze(), np.ones(10)/10, mode='valid')

    # Calcular a segunda derivada do histograma
    second_derivative = np.diff(first_derivative)
    second_derivative = np.convolve(second_derivative.squeeze(), np.ones(10)/10, mode='valid')

    # Plotar os gráficos
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.plot(hist)
    plt.title('Histograma Original')

    plt.subplot(1, 3, 2)
    plt.plot(first_derivative)
    plt.title('Primeira Derivada')

    plt.subplot(1, 3, 3)
    plt.plot(second_derivative)
    plt.title('Segunda Derivada')

    plt.tight_layout()
    plt.show()

def find_path(img, tolerancia_h, tolerancia_s, tolerancia_v, h_min=0, h_max=0, s_min=0, s_max=0, v_min=0, v_max=0, usar_perfil=False):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Criar uma máscara de ponderação para dar mais peso ao centro da img
    rows, cols, _ = img.shape
    center_row, center_col = rows // 2, cols // 2
    weight_mask = np.zeros((rows, cols), dtype=np.float32)

    for i in range(rows):
        for j in range(cols):
            distance = np.sqrt((i - center_row)**2 + (j - center_col)**2)
            weight_mask[i, j] = np.exp(-distance / (0.5 * min(center_row, center_col)))

    weight_mask = cv2.normalize(weight_mask, None, 0, 1, cv2.NORM_MINMAX)

    # Separar os canais H, S e V
    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]

    # Calcular os histogramas ponderados manualmente
    hist_h = np.zeros(180, dtype=np.float32)
    hist_s = np.zeros(256, dtype=np.float32)
    hist_v = np.zeros(256, dtype=np.float32)

    for i in range(rows):
        for j in range(cols):
            hist_h[h_channel[i, j]] += weight_mask[i, j]
            hist_s[s_channel[i, j]] += weight_mask[i, j]
            hist_v[v_channel[i, j]] += weight_mask[i, j]

    # Convoluir os histogramas para suavizar
    hist_h = np.convolve(hist_h, np.array([0, 1, 1, 1, 1, 1, 0]) / 5, mode='valid')
    hist_s = np.convolve(hist_s, np.ones(5)/5, mode='valid')
    hist_v = np.convolve(hist_v, np.ones(5)/5, mode='valid')
    
    # Ignorar os tons de roxo no histograma de matiz (120 a 160)
    hist_h[120:160] = 0

    # Encontrar o valor de matiz (H) mais comum fora do intervalo de roxo
    valor_h_comum = np.argmax(hist_h)
    valor_s_comum = np.argmax(hist_s)
    valor_v_comum = np.argmax(hist_v)
    
    # Definir os limites do intervalo de cor baseados no valor de matiz (H) mais comum
    if not usar_perfil:
        h_min = max(0, valor_h_comum - tolerancia_h)
        h_max = min(255, valor_h_comum + tolerancia_h)
        s_min = max(0, valor_s_comum - tolerancia_s)
        s_max = min(255, valor_s_comum + tolerancia_s)
        v_min = max(0, valor_v_comum - tolerancia_v)
        v_max = min(255, valor_v_comum + tolerancia_v)

    img_blur = cv2.GaussianBlur(hsv, (13, 13), 0)
    img_blur = cv2.GaussianBlur(img_blur, (11, 11), 0)
    img_blur = cv2.GaussianBlur(img_blur, (7, 7), 0)
    img_blur = cv2.GaussianBlur(img_blur, (5, 5), 0)
    img_blur = cv2.GaussianBlur(img_blur, (3, 3), 0)

    lowerb = np.array([h_min, s_min, v_min])
    upperb = np.array([h_max, s_max, v_max])

    # Criar a máscara usando os limites do intervalo de cor
    mascara = cv2.inRange(hsv, lowerb, upperb)

    kernel = np.ones((3,3), np.uint8)
    img_dilatada = cv2.dilate(mascara, kernel, iterations=8)

    kernel = np.ones((3,3), np.uint8)
    img_erodida = cv2.erode(img_dilatada, kernel, iterations=10)
    img_reversed = cv2.bitwise_not(img_erodida)

    contorno = cv2.bitwise_and(img, img, mask=img_reversed)
    
    plt.figure()
    plt.imshow(contorno, cmap="gray")
    plt.axis('off')
    return img_reversed, h_min, h_max, s_min, s_max, v_min, v_max

def save_color_profile(image_path, profile_name, h_min, h_max, s_min, s_max, v_min, v_max, save_directory='color_profiles'):
    # Carregar a img
    image = Image.open(image_path)
    image = image.convert('RGB')
    
    # Converter a img para HSV
    hsv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV)
    
    # Calcular os histogramas
    hist_h = cv2.calcHist([hsv_image], [0], None, [256], [0, 256])
    hist_s = cv2.calcHist([hsv_image], [1], None, [256], [0, 256])
    hist_v = cv2.calcHist([hsv_image], [2], None, [256], [0, 256])
    
    # Normalizar os histogramas
    hist_h = hist_h / hist_h.sum()
    hist_s = hist_s / hist_s.sum()
    hist_v = hist_v / hist_v.sum()
    
    # Criar o perfil de cores
    color_profile = {
        'hist_h': hist_h,
        'hist_s': hist_s,
        'hist_v': hist_v,
        'h_min': h_min,
        'h_max': h_max,
        's_min': s_min,
        's_max': s_max,
        'v_min': v_min,
        'v_max': v_max
    }
    
    # Criar o diretório de perfis de cores, se não existir
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    # Salvar o perfil de cores
    profile_path = os.path.join(save_directory, f'{profile_name}.pkl')
    with open(profile_path, 'wb') as f:
        pickle.dump(color_profile, f)
    
    print(f'Perfil de cores salvo em: {profile_path}')

def compare_color_profile(image_path, save_directory='color_profiles'):
    # Carregar a img
    image = Image.open(image_path)
    image = image.convert('RGB')
    
    # Converter a img para HSV
    hsv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV)
    
    # Calcular os histogramas
    hist_h = cv2.calcHist([hsv_image], [0], None, [256], [0, 256])
    hist_s = cv2.calcHist([hsv_image], [1], None, [256], [0, 256])
    hist_v = cv2.calcHist([hsv_image], [2], None, [256], [0, 256])
    
    # Normalizar os histogramas
    hist_h = hist_h / hist_h.sum()
    hist_s = hist_s / hist_s.sum()
    hist_v = hist_v / hist_v.sum()
    
    # Carregar perfis de cores salvos
    profiles = []
    for filename in os.listdir(save_directory):
        if filename.endswith('.pkl'):
            with open(os.path.join(save_directory, filename), 'rb') as f:
                profiles.append((filename, pickle.load(f)))
    
    # Comparar a img com cada perfil de cores
    max_correlation = -1
    best_match = None
    best_profile = None
    for profile_name, profile in profiles:
        corr_h = cv2.compareHist(hist_h, profile['hist_h'], cv2.HISTCMP_CORREL)
        corr_s = cv2.compareHist(hist_s, profile['hist_s'], cv2.HISTCMP_CORREL)
        corr_v = cv2.compareHist(hist_v, profile['hist_v'], cv2.HISTCMP_CORREL)
        
        # Calcular a média das correlações
        mean_correlation = (corr_h + corr_s + corr_v) / 3
        if mean_correlation > max_correlation:
            max_correlation = mean_correlation
            best_match = profile_name
            best_profile =  profile
    
    return best_match, best_profile['h_min'], best_profile['h_max'], best_profile['s_min'], best_profile['s_max'], best_profile['v_min'], best_profile['v_max']

def path_detection(name, t_h, t_s, t_v):
    _, h_min, h_max, s_min, s_max, v_min, v_max = compare_color_profile(name)
    original_image = Image.open(name)
    cv2_img = np.array(original_image)
    output, h_min, h_max, s_min, s_max, v_min, v_max = find_path(cv2_img, t_h, t_s, t_v, h_min, h_max, s_min, s_max, v_min, v_max, True)
    return output