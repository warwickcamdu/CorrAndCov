
import os
import numpy as np
import matplotlib.pyplot as plt
import javabridge
import bioformats
import tifffile as tif
from matlab_imresize.imresize import imresize


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
        image_normalised = np.zeros((np.ceil(
            [image.shape[0],
             image.shape[1]*scalefactor,
             image.shape[2]*scalefactor])).astype(int))
        for i in range(image.shape[0]):
            # Use Matlab-esque rescaling
            image_rescaled = imresize(image[i, ...], scalar_scale=scalefactor)
            image_normalised[i, ...] = image_rescaled / np.mean(image_rescaled)
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
        scalefactor (float): scale factor to downscale image by

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


def cross_correlation(image1, image2, scalefactor, offset):
    '''
    Auto- and cross-correlation

    Parameters:
        image1, image2 (numpy arrays): images to compare
        offset (int): shift in pixels relative to the reference image
        scalefactor (float): scale factor to upscale image by

    Returns:
        corr (list of floats): list of corrolation values for each offset value
    '''
    if offset > image1.shape[0]:
        offset = image1.shape[0]-1
    corr = np.zeros([offset, image1.shape[1], image1.shape[2]])
    for i in range(0, offset, 1):
        tshift = np.roll(image2, i, axis=0)
        t = image1[i:, :, :] - np.mean(image1[i:, :, :], axis=0)
        tshift = tshift[i:, :, :] - np.mean(tshift[i:, :, :], axis=0)
        total_of_multiple = np.sum(np.multiply(t, tshift), axis=0)
        multipe_of_stds = (np.std(t, axis=0, ddof=1)
                           * np.std(tshift, axis=0, ddof=1))
        corr_small = (total_of_multiple/(tshift.shape[0]-1))/multipe_of_stds
        corr[i, ...] = corr_small
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
    std_t_image = np.std(image, axis=0, ddof=1)
    CoV_map = std_t_image/np.mean(mean_t_image)
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
    x1 = np.copy(CoV_actin)
    y1 = np.copy(corr)
    y1[corr < 0] = 0
    plt.scatter(x1, y1, marker='o', facecolors='none', edgecolors='blue')
    y2 = np.copy(corr)
    y2[corr >= 0] = 0
    plt.scatter(x1, y2, marker='o', facecolors='none', edgecolors='red')
    plt.title(title)
    plt.xlabel('Actin Coeff of Variation')
    plt.ylabel('Cross correlation value')
    plt.xlim((0, 1.5))
    plt.ylim((-1, 1))
    # plt.show()
    fig.savefig(os.path.join(save_location, title+'.png'))
    plt.close()


def calculate_and_create_figures(data_path, actin_folder, scalefactor, offset):
    '''
    Read in data, calculate auto- and cross-correlation and coefficient of
    variance, output images and figures of results.

    Parameters:
        data_path (str): path to folder where data is stored
        actin_folder (str): name of folder containing actin images
        scalefactor (float): scale factor to downscale image by
        offset (int): shift in pixels relative to the reference image

    Returns:
        Saves .png files in folder above data folder
    '''
    try:
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
                    results_path, 'cov_'+im+'_'+ch+'.tif'),
                           imresize(cov, scalar_scale=1/scalefactor))
                if ch == actin_folder:
                    cov_act = cov
            combinations = [tuple(sorted((f, s), reverse=True))
                            for f in image_dict[im].keys()
                            for s in image_dict[im].keys()]
            for c in set(combinations):
                corr = cross_correlation(
                    image_dict[im][c[0]],
                    image_dict[im][c[1]],
                    scalefactor,
                    offset)
                # Rescale corr to original image size
                corr_large = np.zeros([corr.shape[0],
                                      int(corr.shape[1]/scalefactor),
                                      int(corr.shape[2]/scalefactor)])
                for i in range(corr.shape[0]):
                    corr_large[i, ...] = imresize(corr[i, ...],
                                                  scalar_scale=1/scalefactor)
                tif.imsave(os.path.join(results_path, 'corr_'
                           + im+'_'+c[0]+c[1]+'.tif'), corr_large
                           )
                for co in range(corr.shape[0]):
                    if c[0] != c[1]:
                        title = 'CoVA_CC_'+im+'_'+c[0]+c[1]+'_'+str(co)
                        create_scatter_figure(
                            cov_act, corr[co, ...], title, results_path)
    finally:
        end_java_vm()


def main():
    data_path = '/home/laura/WMS_Files/ProjectSupport/DK_Corr/' \
                '3011_ATP_Example/data files'
    scalefactor = 0.25
    offset = 10
    actin_folder = 'actin'
    calculate_and_create_figures(data_path, actin_folder, scalefactor, offset)


if __name__ == "__main__":
    main()
