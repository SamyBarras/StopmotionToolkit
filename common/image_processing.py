import pygame, cv2
import numpy as np

def BGRtoRGB(cv2Image):
    cv2Image[:, :, [0, 2]] = cv2Image[:, :, [2, 0]]
    return cv2Image

def cv2ImageToSurface(cv2Image):
    # from https://stackoverflow.com/questions/64183409/how-do-i-convert-an-opencv-cv2-image-bgr-and-bgra-to-a-pygame-surface-object
    if cv2Image.dtype.name == 'uint16':
        cv2Image = (cv2Image / 256).astype('uint8')
    size = cv2Image.shape[1::-1]
    if len(cv2Image.shape) == 2:
        cv2Image = np.repeat(cv2Image.reshape(size[1], size[0], 1), 3, axis = 2)
        format = 'RGB'
    else:
        format = 'RGBA' if cv2Image.shape[2] == 4 else 'RGB'
        cv2Image[:, :, [0, 2]] = cv2Image[:, :, [2, 0]]
    
    surface = pygame.image.frombuffer(cv2Image.flatten(), size, format)
    return surface.convert_alpha() if format == 'RGBA' else surface.convert()


def rescaleToDisplay(img, display):
    global screen
    ix,iy = (img.shape[1],img.shape[0])
    bx, by = display.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    
    reduced = cv2.resize(img, (int(sx),int(sy)), interpolation=cv2.INTER_AREA)
    return cv2ImageToSurface(reduced)
            
    
def rescaleImg(image, mult):
    scale_percent = mult  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized
