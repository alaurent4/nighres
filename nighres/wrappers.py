from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename

import nibabel as nb
import numpy as np
import os
from nighres.brain.mgdm_segmentation import mgdm_segmentation
from nighres.brain.enhance_region_contrast import enhance_region_contrast
from nighres.surface.probability_to_levelset import probability_to_levelset
from nighres.brain.define_multi_region_priors import define_multi_region_priors
from nighres.filter.recursive_ridge_diffusion import recursive_ridge_diffusion
from nighres.segmentation.lesion_extraction import lesion_extraction


class MGDMSegmentationInputSpec(BaseInterfaceInputSpec):
    contrast_image1 = File(exists=True, desc='specify a first contrast image', mandatory=True)
    contrast_type1  = traits.Str(argstr='%s', desc='type of the image number one', mandatory=True)
    contrast_image2 = File(exists=True, argstr="%s", desc='specify a second contrast image (optionnal)')
    contrast_type2  = traits.Str(argstr='%s', desc='type of the image number two')
    #contrast_image3 = File(exists=True, argstr="%s", desc='specify a third contrast image (optionnal)')
    #contrast_type3  = traits.Str(argstr='%s', desc='type of the image number three')
    #contrast_image4 = File(exists=True, argstr="%s", desc='specify a fourth contrast image (optionnal)')
    #contrast_type4  = traits.Str(argstr='%s', desc='type of the image number four')
    
    #n_steps
    #max_iterations
    #topology='wcs'
                      
    atlas_file = File(exists=True, desc='Path to plain text atlas file', mandatory=True)
    #topology_lut_dir=None,
    #adjust_intensity_priors=False,
    #compute_posterior=False,
    #diffuse_probabilities=False,
    save_data = traits.Bool(True, desc='Save output data to file', usedefault=True)
    output_dir = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    #file_name=None


class MGDMSegmentationOutputSpec(TraitedSpec):
    segmentation = File(exists=True, desc="Hard brain segmentation with topological constraints (if chosen)")
    labels = File(exists=True, desc="Maximum tissue probability labels")
    memberships = File(exists=True, desc="""Maximum tissue probability values, 4D image where the first dimension shows each voxel's highest probability to  belong to a specific tissue, 
                                            the second dimension shows the second highest probability to belong to another tissue etc.""")
    distance = File(exists=True, desc="Minimum distance to a segmentation boundary")


class MGDMSegmentation(BaseInterface):
    input_spec = MGDMSegmentationInputSpec
    output_spec = MGDMSegmentationOutputSpec

    def _run_interface(self, runtime):
        
        mgdm_segmentation(contrast_image1 = self.inputs.contrast_image1,
                          contrast_type1 = self.inputs.contrast_type1,
                          contrast_image2 = self.inputs.contrast_image2,
                          contrast_type2 = self.inputs.contrast_type2,
                          atlas_file = self.inputs.atlas_file,
                          save_data = self.inputs.save_data,
                          output_dir = self.inputs.output_dir)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.contrast_image1
        path, base, ext = split_filename(fname)
        outputs["segmentation"] = os.path.abspath(base + '_mgdm_seg.nii.gz')
        outputs["labels"] = os.path.abspath(base + '_mgdm_lbls.nii.gz')
        outputs["memberships"] = os.path.abspath(base + '_mgdm_mems.nii.gz')
        outputs["distance"] = os.path.abspath(base + '_mgdm_dist.nii.gz')
        return outputs



class EnhanceRegionContrastInputSpec(BaseInterfaceInputSpec):
    
    intensity_image = File(exists=True, desc='specify an intensity image', mandatory=True)
    segmentation_image = File(exists=True, desc='specify a segmentation image', mandatory=True)
    levelset_boundary_image = File(exists=True, desc='specify a levelset boundary image', mandatory=True)
    atlas_file = File(exists=True, desc='Path to plain text atlas file', mandatory=True)
                            
    enhanced_region = traits.Str(argstr='%s', desc='which region you want to extract', mandatory=True)
    contrast_background = traits.Str(argstr='%s', desc='the other region in brain I guess', mandatory=True)
    partial_voluming_distance = traits.Float(desc='partial voluming distance',mandatory=True)
    save_data = traits.Bool(True, desc='Save output data to file', usedefault=True)
    output_dir = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    #file_name

class EnhanceRegionContrastOutputSpec(TraitedSpec):
    
    region_mask = File(exists=True, desc="Hard brain segmentation with topological constraints (if chosen)")
    background_mask = File(exists=True, desc="Hard brain segmentation with topological constraints (if chosen)")
    region_prob = File(exists=True, desc="Hard brain segmentation with topological constraints (if chosen)")
    background_prob = File(exists=True, desc="Hard brain segmentation with topological constraints (if chosen)")
    region_partial_vol = File(exists=True, desc="Hard brain segmentation with topological constraints (if chosen)")


class EnhanceRegionContrast(BaseInterface):
    input_spec = EnhanceRegionContrastInputSpec
    output_spec = EnhanceRegionContrastOutputSpec

    def _run_interface(self, runtime):
        
        enhance_region_contrast(intensity_image = self.inputs.intensity_image,
                                segmentation_image = self.inputs.segmentation_image,
                                levelset_boundary_image = self.inputs.levelset_boundary_image,
                                atlas_file = self.inputs.atlas_file,
                                enhanced_region = self.inputs.enhanced_region,
                                contrast_background = self.inputs.contrast_background,
                                partial_voluming_distance = self.inputs.partial_voluming_distance,
                                save_data = self.inputs.save_data,
                                output_dir = self.inputs.output_dir)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.intensity_image
        path, base, ext = split_filename(fname)
        outputs["region_mask"] = os.path.abspath(base + '_erc_reg.nii.gz')
        outputs["background_mask"] = os.path.abspath(base + '_erc_back.nii.gz')
        outputs["region_prob"] = os.path.abspath(base + '_erc_regProb.nii.gz')
        outputs["background_prob"] = os.path.abspath(base + '_erc_backProb.nii.gz')
        outputs["region_partial_vol"] = os.path.abspath(base + '_erc_regPartVol.nii.gz')
        return outputs
    
    
    
class ProbabilityToLevelsetInputSpec(BaseInterfaceInputSpec):
    
    probability_image = File(exists=True, desc='specify a probability image', mandatory=True)
    save_data = traits.Bool(True, desc='Save output data to file', usedefault=True)
    output_dir = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    #file_name=None)


class ProbabilityToLevelsetOutputSpec(TraitedSpec):
    
    levelset = File(exists=True, desc="")
    

class ProbabilityToLevelset(BaseInterface):
    input_spec = ProbabilityToLevelsetInputSpec
    output_spec = ProbabilityToLevelsetOutputSpec

    def _run_interface(self, runtime):
        
        probability_to_levelset(probability_image = self.inputs.probability_image,
                                save_data = self.inputs.save_data,
                                output_dir = self.inputs.output_dir)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.probability_image
        path, base, ext = split_filename(fname)
        outputs["levelset"] = os.path.abspath(base + '_levelset.nii.gz')
        return outputs
    


class DefineMultiRegionPriorsInputSpec(BaseInterfaceInputSpec):
    
    segmentation_image = File(exists=True, desc='specify a segmentation image', mandatory=True)
    levelset_boundary_image = File(exists=True, desc='specify a levelset boundary image', mandatory=True)
    atlas_file = File(exists=True, desc='Path to plain text atlas file', mandatory=True)
    #defined_region = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    definition_method = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    distance_offset = traits.Float(desc='partial voluming distance',mandatory=True)
    save_data = traits.Bool(True, desc='Save output data to file', usedefault=True)
    output_dir = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    #file_name=None)


class DefineMultiRegionPriorsOutputSpec(TraitedSpec):
    
    intervent = File(exists=True, desc="")
    horns = File(exists=True, desc="")
    intercap = File(exists=True, desc="")
    

class DefineMultiRegionPriors(BaseInterface):
    input_spec = DefineMultiRegionPriorsInputSpec
    output_spec = DefineMultiRegionPriorsOutputSpec

    def _run_interface(self, runtime):
        
        define_multi_region_priors(segmentation_image = self.inputs.segmentation_image,
                                   levelset_boundary_image = self.inputs.levelset_boundary_image,
                                   atlas_file = self.inputs.atlas_file,
                                   #defined_region = self.inputs.defined_region,
                                   definition_method = self.inputs.definition_method,
                                   distance_offset = self.inputs.distance_offset,
                                   save_data = self.inputs.save_data,
                                   output_dir = self.inputs.output_dir)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.segmentation_image
        path, base, ext = split_filename(fname)
        outputs["intervent"] = os.path.abspath(base + '_dmrp_intervent.nii.gz')
        outputs["horns"] = os.path.abspath(base + '_dmrp_horns.nii.gz')
        outputs["intercap"] = os.path.abspath(base + '_dmrp_intercap.nii.gz')
        return outputs
    
    
class RecursiveRidgeDiffusionInputSpec(BaseInterfaceInputSpec):
    
    input_image = File(exists=True, desc='specify an input image', mandatory=True)
    ridge_intensities = traits.Str(argstr='%s', desc='ridge intensities', mandatory=True)
    ridge_filter = traits.Str(argstr='%s', desc='ridge filter', mandatory=True)
    surface_levelset = File(exists=True, desc='specify a distance image', mandatory=True)
    orientation = traits.Str(argstr='%s', desc='orientation', mandatory=True)
    ang_factor = traits.Float(desc='angular factor',mandatory=True)
    loc_prior = File(exists=True, desc='specify a location prior image')
    nb_scales = traits.Int(desc='number of scales', mandatory=True)
    propagation_model = traits.Str(argstr='%s', desc='propagation model', mandatory=True)
    diffusion_factor = traits.Float(desc='diffusion factor',mandatory=True)
    similarity_scale = traits.Float(desc='similarity scale',mandatory=True)
    neighborhood_size = traits.Int(desc='neighborhood size', mandatory=True)
    max_iter = traits.Int(desc='maximum of iterations', mandatory=True)
    max_diff = traits.Float(desc='maximum difference',mandatory=True)
    save_data = traits.Bool(True, desc='Save output data to file', usedefault=True)
    output_dir = traits.Str(argstr='%s', desc='output directory', mandatory=True)
    #file_name=None)


class RecursiveRidgeDiffusionOutputSpec(TraitedSpec):
    
    filter = File(exists=True, desc="")
    proba = File(exists=True, desc="")
    propag = File(exists=True, desc="")
    scale = File(exists=True, desc="")
    direction = File(exists=True, desc="")
    correct = File(exists=True, desc="")
    size = File(exists=True, desc="")
    

class RecursiveRidgeDiffusion(BaseInterface):
    input_spec = RecursiveRidgeDiffusionInputSpec
    output_spec = RecursiveRidgeDiffusionOutputSpec

    def _run_interface(self, runtime):
        
        recursive_ridge_diffusion(input_image = self.inputs.input_image,
                                  ridge_intensities = self.inputs.ridge_intensities,
                                  ridge_filter = self.inputs.ridge_filter,
                                  surface_levelset = self.inputs.surface_levelset,
                                  orientation = self.inputs.orientation,
                                  ang_factor = self.inputs.ang_factor,
                                  loc_prior = self.inputs.loc_prior,
                                  nb_scales = self.inputs.nb_scales,
                                  propagation_model = self.inputs.propagation_model,
                                  diffusion_factor = self.inputs.diffusion_factor,
                                  similarity_scale = self.inputs.similarity_scale,
                                  neighborhood_size = self.inputs.neighborhood_size,
                                  max_iter = self.inputs.max_iter,
                                  max_diff = self.inputs.max_diff,
                                  save_data = self.inputs.save_data,
                                  output_dir = self.inputs.output_dir)
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.input_image
        path, base, ext = split_filename(fname)
        outputs["filter"] = os.path.abspath(base + '_ridge_filter.nii.gz')
        outputs["proba"] = os.path.abspath(base + '_ridge_proba.nii.gz')
        outputs["propag"] = os.path.abspath(base + '_ridge_propag.nii.gz')
        outputs["scale"] = os.path.abspath(base + '_ridge_scale.nii.gz')
        outputs["direction"] = os.path.abspath(base + '_ridge_direction.nii.gz')
        outputs["correct"] = os.path.abspath(base + '_ridge_correct.nii.gz')
        outputs["size"] = os.path.abspath(base + '_ridge_size.nii.gz')
        return outputs
    
    
class LesionExtractionInputSpec(BaseInterfaceInputSpec):
    
    
    probability_image = File(exists=True, desc='specify a probability image', mandatory=True)
    segmentation_image = File(exists=True, desc='specify a segmentation image', mandatory=True)
    levelset_boundary_image = File(exists=True, desc='specify a distance image', mandatory=True)
    location_prior_image = File(exists=True, desc='specify a location prior image', mandatory=True)
    atlas_file = File(exists=True, desc='Path to plain text atlas file', mandatory=True)
    gm_boundary_partial_vol_dist = traits.Float(desc='gm_boundary_partial_vol_dist',mandatory=True)
    csf_boundary_partial_vol_dist = traits.Float(desc='csf_boundary_partial_vol_dist',mandatory=True)
    lesion_clust_dist = traits.Float(desc='lesion_clust_dist',mandatory=True)
    prob_min_thresh = traits.Float(desc='prob_min_thresh',mandatory=True)
    prob_max_thresh = traits.Float(desc='prob_max_thresh',mandatory=True)
    small_lesion_size = traits.Float(desc='small_lesion_size',mandatory=True)
    save_data = traits.Bool(True, desc='Save output data to file', usedefault=True)
    output_dir = traits.Str(argstr='%s', desc='output directory', mandatory=True)    
    #file_name=None)


class LesionExtractionOutputSpec(TraitedSpec):
    
    region = File(exists=True, desc="")
    lesion_size = File(exists=True, desc="")
    lesion_proba = File(exists=True, desc="")
    boundary = File(exists=True, desc="")
    label = File(exists=True, desc="")
    score = File(exists=True, desc="")
    

class LesionExtraction(BaseInterface):
    input_spec = LesionExtractionInputSpec
    output_spec = LesionExtractionOutputSpec

    def _run_interface(self, runtime):
        
        lesion_extraction(probability_image = self.inputs.probability_image,
                          segmentation_image = self.inputs.segmentation_image,
                          levelset_boundary_image = self.inputs.levelset_boundary_image,
                          location_prior_image = self.inputs.location_prior_image,
                          atlas_file = self.inputs.atlas_file,
                          gm_boundary_partial_vol_dist = self.inputs.gm_boundary_partial_vol_dist,
                          csf_boundary_partial_vol_dist = self.inputs.csf_boundary_partial_vol_dist,
                          lesion_clust_dist = self.inputs.lesion_clust_dist,
                          prob_min_thresh = self.inputs.prob_min_thresh,
                          prob_max_thresh = self.inputs.prob_max_thresh,
                          small_lesion_size = self.inputs.small_lesion_size,
                          save_data = self.inputs.save_data,
                          output_dir = self.inputs.output_dir)
                      
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.probability_image
        path, base, ext = split_filename(fname)
        outputs["region"] = os.path.abspath(base + '_extract_reg.nii.gz')
        outputs["lesion_size"] = os.path.abspath(base + '_extract_legSize.nii.gz')
        outputs["lesion_proba"] = os.path.abspath(base + '_extract_legProb.nii.gz')
        outputs["boundary"] = os.path.abspath(base + '_extract_bound.nii.gz')
        outputs["label"] = os.path.abspath(base + '_extract_label.nii.gz')
        outputs["score"] = os.path.abspath(base + '_extract_score.nii.gz')
        return outputs