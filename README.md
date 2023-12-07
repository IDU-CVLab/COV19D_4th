[![DOI:10.48550/arXiv.2210.02992](http://img.shields.io/badge/DOI-10.48550/arXiv.2310.08165-B31B1B.svg)](https://doi.org/10.48550/arXiv.2310.08165)  

# DataBase
COV19-CT Database was shared in the third run of the competition and can be obtained from the workshop organizers at [https://mlearn.lincoln.ac.uk/icassp-2023-ai-mia/](https://mlearn.lincoln.ac.uk/icassp-2023-ai-mia/).

# Method
This code can be deployed in either of two ways; without CT images processing (you may skip this step in the Code), or with images processing:  </br></br>
**Image Processing Phase (Optional).** Images were processed by deletion of nonrepresentative slcies in each CT scan and region of interest (ROI) cropping of the slices.  </br>  
**Vision Trnasformer for Slices Diagnosis.** Vision Trnasformer-based methodology (swin_base_patch4_window12_384) was used to make diagnosis decisions at slices level. At patient level, different thresholds were tested to make final diagnostic decisions for each patient.  </br> </br> 
* Please note: This is a binary classification task. To replicate the method on multi-class classification data, you need to modify the model's output to suit your task.  
* Please refer to the attached paper for more details on the methodology.

# Dependencies
torch==1.10.1+cu102  
torchvision==0.11.2+cu102  
timm==0.6.12  
pil==8.3.1   

# Citation
If you find the this method useful, please consider citing:  
@misc{morani2023covid19,  
      title={COVID-19 Detection Using Swin Transformer Approach from Computed Tomography Images},  
      author={Kenan Morani},  
      year={2023},  
      eprint={2310.08165},  
      archivePrefix={arXiv},  
      primaryClass={eess.IV}  
}
