import numpy as np
import nibabel as nb
import os
import sys
import cbstools
from ..io import load_volume, save_volume
from ..utils import _output_dir_4saving, _fname_4saving


def distance_based_probability(segmentation_image, #probability_image,
                               #bg_dist_mm, bg_proba, dist_ratio,
                               #bg_included, 
                               proba_merging,
                               save_data=False, output_dir=None,
                               file_name=None):

    """ Distance based probability

    Compute a distance boundary map from a probability image.

    Parameters
    ----------
    probability_image: niimg

	segmentation_image: niimg

    bg_dist_mm: float
        MGDM distance to closest boundary (_mgdm_dist)

	bg_proba: float
	   
	dist_ratio: float

	bg_included: float

	proba_merging: float
	
    
    Returns
    ----------
   	dict
        Dictionary collecting outputs under the following keys
        (suffix of output files in brackets)

        * prob_image (niimg): 
        * mgdm_image (niimg): 
        * bg_mask (niimg): 
        * label_number (niimg): 

    Notes
    ----------
    Original Java module by Pierre-Louis Bazin. 

    References
    ----------

    """

    print('\n Distance Based Probability')

    # make sure that saving related parameters are correct
    if save_data:
        output_dir = _output_dir_4saving(output_dir, segmentation_image)

        prob_image_file = _fname_4saving(file_name=file_name,
                                  rootfile=segmentation_image,
                                  suffix='prob_image')
        
        max_label_file = _fname_4saving(file_name=file_name,
                                  rootfile=segmentation_image,
                                  suffix='max_label')

        mgdm_image_file = _fname_4saving(file_name=file_name,
                                  rootfile=segmentation_image,
                                  suffix='mgdm_image')

        bg_mask_file = _fname_4saving(file_name=file_name,
                                   rootfile=segmentation_image,
                                   suffix='bg_mask')

        #label_number_file = _fname_4saving(file_name=file_name,
        #                           rootfile=segmentation_image,
        #                           suffix='labels')

    # start virtual machine, if not already running
    try:
        cbstools.initVM(initialheap='6000m', maxheap='6000m')
    except ValueError:
        pass
    # create extraction instance
    dbp = cbstools.SegmentationDistanceBasedProbability()

    # set extraction parameters
    #dbp.setBackgroundDistance_mm(bg_dist_mm)
    #dbp.setBackgroundProbability(bg_proba)
    #dbp.setDistanceRatio(dist_ratio)
    #dbp.setBackgroundIncluded(bg_included)
    dbp.setProbabilityMerging(proba_merging)
    

    # load segmentation image and use it to set dimensions and resolution
    img = load_volume(segmentation_image)
    data = img.get_data()
    affine = img.get_affine()
    header = img.get_header()
    resolution = [x.item() for x in header.get_zooms()]
    dimensions = data.shape

    dbp.setDimensions(dimensions[0], dimensions[1], dimensions[2])
    dbp.setResolutions(resolution[0], resolution[1], resolution[2])

    # input segmentation image
    dbp.setSegmentationImage(cbstools.JArray('int')((data.flatten('F')).astype(int)))

    # input prior probability image
    #data = load_volume(probability_image).get_data()
    #dbp.setPriorProbabilityImage(cbstools.JArray('float')((data.flatten('F')).astype(float)))
    

    # execute Extraction
    try:
        dbp.execute()

    except:
        # if the Java module fails, reraise the error it throws
        print("\n The underlying Java code did not execute cleanly: ")
        print sys.exc_info()[0]
        raise
        return

    # reshape output to what nibabel likes
    dimensions4d = [dimensions[0], dimensions[1], dimensions[2], 4]
    prob_image_data = np.reshape(np.array(dbp.getProbabilityImage(),
                                   dtype=np.float32), dimensions4d, 'F')
    
    max_label_data = np.reshape(np.array(dbp.getMaxLabelImage(),
                                   dtype=np.int32), dimensions4d, 'F')
    
    bg_mask_data = np.reshape(np.array(dbp.getBackgroundMaskImage(),
                                    dtype=np.int32), dimensions, 'F')
    
    mgdm_image_data = np.reshape(np.array(dbp.getMgdmImage(),
                                    dtype=np.float32), dimensions, 'F')
    
    #label_number_data = dbp.getLabelNumber()
    
    #max_proba_data = np.reshape(np.array(dbp.getMaxProbaNumber(),
    #                               dtype=np.int32), dimensions4d, 'F')
      
    
    # adapt header max for each image so that correct max is displayed
    # and create nifti objects
    header['cal_max'] = np.nanmax(prob_image_data)
    prob_image = nb.Nifti1Image(prob_image_data, affine, header)
    
    header['cal_max'] = np.nanmax(max_label_data)
    max_label = nb.Nifti1Image(max_label_data, affine, header)

    header['cal_max'] = np.nanmax(bg_mask_data)
    bg_mask = nb.Nifti1Image(bg_mask_data, affine, header)

    header['cal_max'] = np.nanmax(mgdm_image_data)
    mgdm_image = nb.Nifti1Image(mgdm_image_data, affine, header)

    #header['cal_max'] = np.nanmax(label_number_data)
    #label_number = nb.Nifti1Image(label_number_data, affine, header)
    

    if save_data:
        save_volume(os.path.join(output_dir, prob_image_file), prob_image)
        save_volume(os.path.join(output_dir, max_label_file), max_label)
        save_volume(os.path.join(output_dir, bg_mask_file), bg_mask)
        save_volume(os.path.join(output_dir, mgdm_image_file), mgdm_image)
        #save_volume(os.path.join(output_dir, label_number_file), label_number)

    return {'prob_image': prob_image, 'max_label': max_label,
            'bg_mask': bg_mask, 'mgdm_image': mgdm_image}#, 'label_number': label_number}
