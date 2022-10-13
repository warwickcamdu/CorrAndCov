# dkCorr functions, pseudo code
import os
import numpy as np
import matplotlib.pyplot as plt
import javabridge
import bioformats
from skimage.transform import rescale
import tifffile as tif

# Define parameters:
scalefactor = 0.2
offset = 60
# data_path = /path/to/data
# Code assumes there are multiple folders with same named image files


def start_java_vm():
    '''
    Start javabridge so bioformats works
    '''
    javabridge.start_vm(class_path=bioformats.JARS, run_headless=True)


def end_java_vm():
    '''
    Stop javabridge
    '''
    javabridge.kill_vm()


def load_image(image_path):
    '''
    Load 2D+t images to an numpy array using bioformats

    Parameters:
        image_path (str): location of image to open

    Returns:
        image (array): image represented as an array with dimensions [t,x,y]
    '''
    # Get metadata
    xml_string = bioformats.get_omexml_metadata(image_path)
    ome = bioformats.OMEXML(xml_string)
    raw_data = []
    with bioformats.ImageReader(image_path) as rdr:
        for t in range(ome.image().Pixels.get_SizeT()):
            # Don't rescale intensities
            raw_image = rdr.read(t=t, rescale=False)
            raw_data.append(raw_image)
    image = np.array(raw_data)
    return image


def coarse_grain_and_normalise(image_path, scalefactor):
    '''
    Load image, rescale and normalise.

    Parameters:
        image_path (str): location of image to open
        scalefactor (float, tuple of floats): scale factor to downsize image by

    Returns:
        image_normalised (array): image rescaled and normalised by mean
    '''
    # Make this float only and force not scaling of time dimension?
    if (type(scalefactor) is float and scalefactor < 1):
        image = load_image(image_path)
        # Assumes image dimensions [t,x,y], bicubic interpolation
        image_rescaled = rescale(
            image, (1, scalefactor, scalefactor), anti_aliasing=False, order=3)
        image_normalised = np.zeros_like(image_rescaled)
        for i in range(image_rescaled.shape[0]):
            image_normalised[i, ...] = image_rescaled[i, ...] / \
                np.mean(image_rescaled[i, ...])
    else:
        print('scalefactor should be less than 1')
    return image_normalised


def get_names(data_path):
    '''
    Get names of folders and images in data_path

    Parameters:
        data_path (str): path to folder where data is stored

    Returns:
        folders (list of str): list of folders in data_path
        imlist (list of str): list of filenames in first folder
    '''
    folders = os.listdir(data_path)
    imlist = os.listdir(os.path.join(data_path, folders[0]))
    return folders, imlist


def create_image_dictionary(data_path, scalefactor):
    '''
    Creates a dictionary containing all the normalised images and their names

    Parameters:
        data_path (str): path to folder where data is stored
        scalefactor (float, tuple of floats): scale factor to downsize image by

    Returns:
        image_dict (dict): names and normalised images e.g.
        image_dict['3011_SLB3_12sec.tif']['actin'] would return the numpy array
        of the actin channel of image 3011_SLB3_12sec.tif
    '''
    image_dict = {}
    [folders, imlist] = get_names(data_path)
    for im in imlist:
        im_noext = os.path.splitext(im)[0]
        image_dict[im_noext] = dict.fromkeys(folders)
        for folder in folders:
            image_dict[im_noext][folder] = coarse_grain_and_normalise(
                    os.path.join(data_path, folder, im), scalefactor)
    return image_dict


def cross_correlation(image1, image2, offset):
    '''
    Auto- and cross-correlation

    Parameters:
        image1, image2 (numpy arrays): images to compare
        offset (int): shift in pixels relative to the reference image

    Returns:
        corr (list of floats): list of corrolation values for each offset value
    '''
    corr = np.zeros([offset+1, int((1/scalefactor)*image1.shape[1]),
                    int((1/scalefactor)*image1.shape[2])])
    for i in range(offset+1):
        tshift = np.roll(image2, i, axis=0)
        t = image1[i+1:, :, :] - np.mean(image1[i+1:, :, :], axis=0)
        tshift = tshift[i+1:, :, :] - np.mean(tshift[i+1:, :, :], axis=0)
        corr_small = (np.sum(np.multiply(t, tshift), axis=0)
                      / (tshift.shape[0]))/(np.std(t, axis=0)*np.std(tshift, axis=0))
        corr[i, ...] = rescale(corr_small, 1/scalefactor,
                               anti_aliasing=False, order=3)
    return corr


def coefficient_of_variation(image, scalefactor):
    '''
    Calculate coefficient of variation

    Parameters:
        image (numpy array): 2D+t image
        scalefactor (float): scale factor to upscale resulting CoV image

    Returns:
        CoV_map (numpy array): Calculated CoV (2D)
    '''
    # Calculate coefficinet of variation
    mean_t_image = np.mean(image, axis=0)
    std_t_image = np.std(image, axis=0)
    CoV_map = std_t_image/np.mean(mean_t_image)
    CoV_map = rescale(CoV_map, 1/scalefactor, anti_aliasing=False, order=3)
    return CoV_map


def create_scatter_figure(CoV_actin, corr, title, save_location):
    '''
    Plot actin coefficient of variation against cross-correlation values and
    save figure

    Parameters:
        CoV_actin (numpy array): coefficient of variation for actin channel
        corr (numpy array): Cross-correlation values from another channel
        title (string): Title of figure
        save_location (string): Path to location to save data

    Returns:
        Saves .png file in save_location
    '''
    fig = plt.figure()
    plt.scatter(CoV_actin[corr >= 0], corr[corr >= 0],
                marker='o', facecolors='none', edgecolors='blue')
    plt.scatter(CoV_actin[corr < 0], corr[corr < 0],
                marker='o', facecolors='none', edgecolors='red')
    plt.title(title)
    plt.xlabel('Actin Coeff of Variation')
    plt.ylabel('Cross correlation value')
    plt.xlim((0, 1.5))
    plt.ylim((-1, 1))
    # plt.show()
    fig.savefig(os.path.join(save_location, title+'.png'))
    plt.close()


def main():
    '''
    Read in data, calculate auto- and cross-correlation and coefficient of
    variance, output images and figures of results.
    '''
    try:
        data_path = '/home/laura/WMS_Files/ProjectSupport/DK_Corr/3011_ATP_Example/data files'
        scalefactor = 0.2
        actin_folder = 'actin'
        # run steps
        start_java_vm()
        image_dict = create_image_dictionary(data_path, scalefactor)
        for im in image_dict.keys():
            results_path = os.path.join(os.path.dirname(data_path), 'corr_'+im)
            if not os.path.exists(results_path):
                os.makedirs(results_path)
            for ch in image_dict[im].keys():
                cov = coefficient_of_variation(image_dict[im][ch], scalefactor)
                tif.imsave(os.path.join(
                    results_path, 'cov_'+im+'_'+ch+'.tif'), cov)
                if ch == actin_folder:
                    cov_act = cov
            combinations = [tuple(sorted((f, s))) for f in image_dict[im].keys()
                            for s in image_dict[im].keys()]
            for c in set(combinations):
                corr = cross_correlation(
                    image_dict[im][c[0]], image_dict[im][c[1]], 10)
                tif.imsave(os.path.join(results_path, 'corr_'
                           + im+'_'+c[0]+c[1]+'.tif'), corr)
                for co in range(corr.shape[0]):
                    if c[0] != c[1]:
                        title = 'CoVA_CC_'+im+'_'+c[0]+c[1]+'_'+str(co)
                        create_scatter_figure(
                            cov_act, corr[co, ...], title, results_path)
    finally:
        end_java_vm()


if __name__ == "__main__":
    main()
