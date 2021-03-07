import pygame, cv2, os, subprocess, logging
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
    bx, by = (display[0], display[1])
    if ix > bx:
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


def compileAnimation(wdir, frames, name): #channel
    # global HQFilesDir, workingdir
    HQFilesDir = os.path.join(wdir,"HQ")
    command = "ffmpeg -framerate 12 -f image2 -start_number 0 -i {}/{}_%05d.png -vcodec libx264 -pix_fmt yuv420p {}/{}_animation.mp4".format(HQFilesDir, name, wdir, name)
    if (len(frames) > 1) :
        logging.info("Compiling frames as videofile...")
        subprocess.call(command, shell=True)
        logging.info("Animation compiled.")
    else :
        logging.warning("No files to compile as videofile.")
    return True

def centerScreen(screen_res, window_res):
    x = screen_res[0]/2 - window_res[0]/2
    y = screen_res[1]/2 - window_res[1]/2
    return (x, y)


# color correction attempt
def hist_match(source, template):
    """
    Adjust the pixel values of a grayscale image such that its histogram
    matches that of a target image

    Arguments:
    -----------
        source: np.ndarray
            Image to transform; the histogram is computed over the flattened
            array
        template: np.ndarray
            Template image; can have different dimensions to source
    Returns:
    -----------
        matched: np.ndarray
            The transformed output image
    """
    oldshape = source.shape
    source = source.ravel()
    template = template.ravel()
    # get the set of unique pixel values and their corresponding indices and counts
    s_values, bin_idx, s_counts = np.unique(source, return_inverse=True, return_counts=True)
    t_values, t_counts = np.unique(template, return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)
    return interp_t_values[bin_idx].reshape(oldshape)

def colorCorrect () :
    # Read original image
    im_o = cv2.imread('/media/Lexar/color_transfer_data/5/frame10.png')
    im = im_o
    cv2.imshow('Org', im)
    cv2.waitKey()

    B = im[:,:, 0]
    G = im[:,:, 1]
    R = im[:,:, 2]

    R= np.array(R).astype('float')
    G= np.array(G).astype('float')
    B= np.array(B).astype('float')

    # Extract pixels that correspond to pure white R = 255, G = 255, B = 255
    B_white = R[168, 351]
    G_white = G[168, 351]
    R_white = B[168, 351]

    # Compensate for the bias using normalization statistics
    R_balanced = R / R_white
    G_balanced = G / G_white
    B_balanced = B / B_white

    R_balanced[np.where(R_balanced > 1)] = 1
    G_balanced[np.where(G_balanced > 1)] = 1
    B_balanced[np.where(B_balanced > 1)] = 1

    B_balanced=B_balanced * 255
    G_balanced=G_balanced * 255
    R_balanced=R_balanced * 255

    B_balanced= np.array(B_balanced).astype('uint8')
    G_balanced= np.array(G_balanced).astype('uint8')
    R_balanced= np.array(R_balanced).astype('uint8')

    im[:,:, 0] = (B_balanced)
    im[:,:, 1] = (G_balanced)
    im[:,:, 2] = (R_balanced)

    # Notice saturation artifacts 
    cv2.imshow('frame',im)
    cv2.waitKey()

    # Extract the Y plane in original image and match it to the transformed image 
    im_o = cv2.cvtColor(im_o, cv2.COLOR_BGR2YCR_CB)
    im_o_Y = im_o[:,:,0]

    im = cv2.cvtColor(im, cv2.COLOR_BGR2YCR_CB)
    im_Y = im[:,:,0]

    matched_y = hist_match(im_o_Y, im_Y)
    matched_y= np.array(matched_y).astype('uint8')
    im[:,:,0] = matched_y

    im_final = cv2.cvtColor(im, cv2.COLOR_YCR_CB2BGR)
    cv2.imshow('frame', im_final)
    cv2.waitKey()

def white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result