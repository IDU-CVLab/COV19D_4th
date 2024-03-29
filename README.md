# DataBase
COV19-CT Database was shared in the forth run of the competition and can be obtained from the workshop organizers at [https://mlearn.lincoln.ac.uk/ai-mia-cov19d-competition/](https://mlearn.lincoln.ac.uk/ai-mia-cov19d-competition/).

# Method
This code can be deployed in either of two ways: without CT images processing (you may skip this step in the code) or with images processing:  </br></br>
**Images Processing (Optional).** Images were processed by deleting non-representative slices in each CT scan, and cropping the Region Of Interest (ROI) , i.e. the lung areas.  </br>  
**Vision Trnasformer for Slices Diagnosis.** Vision Trnasformer-based methodology (xxs mobile ViT Transformer) was used to make diagnosis decisions at the slice level. Next, majority voting was used to make the final diagnostic decisions for each patient.  </br> </br> 
* Please note: This is a binary classification task. To replicate the method on multi-class classification data, you need to modify the model's output to suit your task.  
* Please refer to the attached paper for more details on the methodology.
* Kindly inform the organization owner if you wish to obtain the pretrained model in this study.  

# Dependencies
torch==1.10.1  
torchvision==0.11.2  
timm==0.6.12   
pil==8.3.1   

# Citation
If you find the this method useful, please consider citing:  
>@misc{morani2023covid19,  
      title={COVID-19 Detection Using Swin Transformer Approach from Computed Tomography Images},  
      author={Kenan Morani},  
      year={2023},  
      eprint={2310.08165},  
      archivePrefix={arXiv},  
      primaryClass={eess.IV}  
}
