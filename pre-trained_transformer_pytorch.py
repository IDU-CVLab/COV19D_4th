# -*- coding: utf-8 -*-


######################## Images Processing #######################
#######################################################################################


### Slices Deletion
import os
import cv2
import re

# Define path of images to be processed
train_dir = '/home/idu/Desktop/COV19D/train-processed/covid/'
val_dir = '/home/idu/Desktop/COV19D/val-processed/val/non-covid/'

main_dir = train_dir

# Define the percentage of images to delete
percentage_to_delete = 40  # Adjust this value as needed

# Function to calculate the number of images to delete
def calculate_images_to_delete(total_count):
    images_to_delete = int((percentage_to_delete / 100) * total_count)
    return images_to_delete

# Function to extract the image number from the filename
def extract_image_number(filename):
    match = re.match(r"(\d+).jpg", filename)
    if match:
        return int(match.group(1))
    return None

# Process each subfolder in the main directory

for subfolder in os.listdir(main_dir):
    subfolder_path = os.path.join(main_dir, subfolder)
    
    if os.path.isdir(subfolder_path):
        # List all files in the subfolder
        files = os.listdir(subfolder_path)
        files.sort(key=lambda x: extract_image_number(x))  # Sort files by image number
        
        total_count = len(files)
        
        if total_count > 1:
            images_to_delete = calculate_images_to_delete(total_count)
            
            print(f"Processing subfolder: {subfolder}")
            
            # Print the list of files before deletion
            print("Files before deletion:", files)
            
            # Delete a percentage of images, keeping centered ones
            for i in range(images_to_delete):
                # Delete images at the beginning and end
                file_to_delete_first = os.path.join(subfolder_path, files[i])
                file_to_delete_last = os.path.join(subfolder_path, files[-(i + 1)])
                print(f"Deleting image: {file_to_delete_first}")
                print(f"Deleting image: {file_to_delete_last}")
                os.remove(file_to_delete_first)
                os.remove(file_to_delete_last)
            
            # Print the list of files after deletion
            files_after_deletion = os.listdir(subfolder_path)
            print("Files after deletion:", files_after_deletion)

print("Deletion process completed.")


### Slices Cropping

#path for images to be processed
folder_path = val_dir

# Specify the new size and cropping position
new_height = 227
new_width = 300
crop_x = 99
crop_y = 160

for sub_folder in os.listdir(folder_path):
    sub_folder_path = os.path.join(folder_path, sub_folder)
    
    print(f'Processing subfolder: {sub_folder}')
    
    for file_name in os.listdir(sub_folder_path):
        file_path = os.path.join(sub_folder_path, file_name)
        
        # Check if the file is an image (you can add more image extensions if needed)
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            #print(f'Processing file: {file_name}')
            
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)  # Load the image in grayscale
            
            # Check if the image was loaded successfully
            if img is not None:
                # Crop the image
                img_cropped = img[crop_y:crop_y+new_height, crop_x:crop_x+new_width]
                
                # Save the cropped image by overwriting the original image
                cv2.imwrite(file_path, img_cropped)
                
                #print(f'Cropped and saved: {file_name}')
            else:
                print(f'Failed to load image: {file_name}')

print('finished')


######################## A transformer for classification########################
#####################################################################################
#######################################################################################3
#!pip install swin_transformer

#!pip install timm

import torch
import torchvision
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import timm
import sys
import PIL
from PIL import Image

import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt

import os
from torch.utils.data import Dataset, DataLoader


class CustomDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = sorted(os.listdir(root_dir))
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        self.images = self.load_images()

    def load_images(self):
        images = []
        for class_name in self.classes:
            class_path = os.path.join(self.root_dir, class_name)
            for ct_scan_folder in os.listdir(class_path):
                ct_scan_path = os.path.join(class_path, ct_scan_folder)
                for img_name in os.listdir(ct_scan_path):
                    img_path = os.path.join(ct_scan_path, img_name)
                    label = self.class_to_idx[class_name]
                    images.append((img_path, label))
        return images

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path, label = self.images[idx]
        image = Image.open(img_path)
        if self.transform:
            image = self.transform(image)
        return image, label


# Define hyperparameters
learning_rate = 0.001
num_epochs = 10
batch_size = 32
# Change input images shape to fit the transformer architecture
img_height = img_width = 384
#img_height = img_width = 224
num_classes = 2

# Define transformations for the images
transform = transforms.Compose([
    transforms.Resize((img_height, img_width)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# Set paths
train_dir = '/home/idu/Desktop/COV19D/train-processed/'
val_dir = '/home/idu/Desktop/COV19D/val-processed/val/'

# Load the validation dataset using the custom dataset class
train_dataset = CustomDataset(train_dir, transform=transform)
val_dataset = CustomDataset(val_dir, transform=transform)

# Create the validation data loader
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

# Set device
device = torch.device("cpu")
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

### Choose a Transformer
## Swin Transformer model
model = timm.create_model('swin_base_patch4_window12_384', pretrained=True, num_classes=num_classes, in_chans=1)
#model = timm.create_model('swin_small_patch4_window7_224', pretrained=True, num_classes=num_classes, in_chans=1)
#model = timm.create_model('swin_tiny', pretrained=True, num_classes=num_classes, in_chans=1)
#model.head.in_features = 1  # Change this if your input has a different number of channels
## ViT model
#model = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=num_classes, in_chans=1)
#model = timm.create_model('vit_small_patch16_224', pretrained=True, num_classes=num_classes, in_chans=1)
#model = timm.create_model('mobilevit_xxs', pretrained=True, num_classes=num_classes, in_chans=1)

model.to(device)

# Define the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

best_val_accuracy = 0.0  # Variable to track the best validation accuracy
best_model_path = '/home/idu/Desktop/COV19D/saved-models/Transformers/imageprocess-swin_base_patch4_window12_384.pt'  # Path to save the best model
#best_model_path = '/home/idu/Desktop/COV19D/saved-models/Transformers/imageprocessedswin_small_patch4_window7_224.pt'  # Path to save the best model


# Checking class labels matching the classes
for images, labels in train_loader:
    print(labels)
    break

for images, labels in val_loader:
    print(labels)
    break


class_order = val_dataset.class_to_idx
print("Class Order:", class_order)

counter = 1
# Train the model
from sklearn.metrics import precision_score, recall_score

for epoch in range(num_epochs):
    print('epoch starts')
    model.train()
    total_loss = 0.0
    total_correct = 0
    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)
                
        # Check labels for invalid values
        assert torch.max(labels) < num_classes, "Invalid label value"
    
        # Forward pass
        outputs = model(images)

        # Compute loss
        loss = criterion(outputs, labels)
        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # Update statistics
        total_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs, 1)
        total_correct += (predicted == labels).sum().item()
        #print(f'{counter} - 6')
        counter += 1
    # Calculate average loss and accuracy for the epoch
    avg_loss = total_loss / len(train_loader.dataset)
    accuracy = total_correct / len(train_loader.dataset)
    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
    
    # Validation
    print('val starts')
    model.eval()
    val_loss = 0.0
    val_correct = 0
    true_labels = []
    predicted_labels = []
    
    with torch.no_grad():
        #print('8')
        for images, labels in val_loader:
            #print('val')
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            val_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            val_correct += (predicted == labels).sum().item()

            true_labels.extend(labels.cpu().numpy())
            predicted_labels.extend(predicted.cpu().numpy())
            
    avg_val_loss = val_loss / len(val_loader.dataset)
    val_accuracy = val_correct / len(val_loader.dataset)
    
    # Calculate precision and recall
    precision = precision_score(true_labels, predicted_labels, average=None)
    recall = recall_score(true_labels, predicted_labels, average=None)
    precision_micro = precision_score(true_labels, predicted_labels, average='micro')
    recall_micro = recall_score(true_labels, predicted_labels, average='micro')

    
    if val_accuracy > best_val_accuracy:
        # Update the best validation accuracy and save the model
     best_val_accuracy = val_accuracy
     torch.save(model.state_dict(), best_model_path)

    print(f"Validation Loss: {avg_val_loss:.4f}, Validation Accuracy: {val_accuracy:.4f}")
    print("Validation Precision:", precision)
    print("Validation micro Precision:", precision_micro)
    print("Validation Recall:", recall)
    print("Validationmicro  Recall:", recall_micro)
    

# Save the trained model fully
#torch.save(model.state_dict(), "/home/idu/Desktop/COV19D/saved-models/transformer_Model.pt")
# save full model including architecture
#torch.save(model, "/home/idu/Desktop/COV19D/ChatGPT-saved-models/Swin-Transformer-model.pt")

#### Evaluating the Model

# Define the path to the saved model file
model_path = best_model_path

# Create an instance of the model class (The borrowed transformer  structure)
model = timm.create_model('swin_base_patch4_window12_384', pretrained=True, num_classes=num_classes, in_chans=1)
    
# Load the saved model weights
model.load_state_dict(torch.load(model_path))

# Set the model to evaluation mode
model.eval()

# Making Predictions
# Define the folder path containing the CT images
#folder_path = '/home/idu/Desktop/COV19D/val-preprocessed/covid'
folder_path = '/home/idu/Desktop/COV19D/train-processed/covid'

covid_predictions = []
noncovid_predictions = []

covid_folder_counts = []
noncovid_folder_counts = []

covid_folder_counts_fourty = []
noncovid_folder_counts_fourty = []

covid_folder_counts_twenty = []
noncovid_folder_counts_twenty = []

covid_folder_counts_five = []
noncovid_folder_counts_five = []

# Iterate through the image files
for fldr in os.listdir(folder_path):
    sub_folder_path = os.path.join(folder_path, fldr)
    for filee in os.listdir(sub_folder_path):
        file_path = os.path.join(sub_folder_path, filee)

        # Load and preprocess the image
        img = Image.open(file_path)
        #img = cv2.imread(file_path)
        img = transform(img)
        img = img.unsqueeze(0)  # Add batch dimension

        # Pass the image through the model to get predictions
        with torch.no_grad():
            output = model(img)
            
        # Print the model's output
        print("Model Output:", output)

        # Interpret the model's output to make predictions
        _, predicted_class = output.max(1)
        #print('predicted class', predicted_class)
        print('predicted class', predicted_class.item())
        
        # Append the prediction to the corresponding list
        if predicted_class.item() == 0:
            covid_predictions.append(0)
        else:
            noncovid_predictions.append(0) 
        # Append the prediction to the corresponding list
        #if predicted_class == 0:
            covid_predictions.append(0)
        #else:
            noncovid_predictions.append(0)
        # Append the count of predicted COVID-19 slices and non-COVID slices for this folder
        
        
    if len(covid_predictions) > len(noncovid_predictions):
     print('COVID patinet')
     covid_folder_counts.append(file_path)
    else:
     noncovid_folder_counts.append(file_path)
     print('non-COVID patient')
     
    if len(covid_predictions) > 0.4 * len(noncovid_predictions):
      covid_folder_counts_fourty.append(file_path)
    else:
      noncovid_folder_counts_fourty.append(file_path)
      
    if len(covid_predictions) > 0.2 * len(noncovid_predictions):
      covid_folder_counts_twenty.append(file_path)
    else:
      noncovid_folder_counts_twenty.append(file_path)
      
    if len(covid_predictions) > 0.05 * len(noncovid_predictions):
      covid_folder_counts_five.append(file_path)
    else:
      noncovid_folder_counts_five.append(file_path)

    # Create empty lists to store the counts of predicted COVID-19 and non-COVID CT folders
    covid_predictions = []
    noncovid_predictions = []
    
   

# Print the lists of CT folder counts (COVID-19 and non-COVID)
#print("List of COVID-19 Folder Counts:", covid_folder_counts)
#print("List of Non-COVID Folder Counts:", noncovid_folder_counts)

print("Length of COVID-19 Folder Counts:", len(covid_folder_counts))
print("Length of Non-COVID Folder Counts:", len(noncovid_folder_counts))

print("Length of COVID-19 Folder Counts 40%:", len(covid_folder_counts_fourty))
print("Length of Non-COVID Folder Counts40% :", len(noncovid_folder_counts_fourty))

print("Length of COVID-19 Folder Counts 20%:", len(covid_folder_counts_twenty))
print("Length of Non-COVID Folder Counts 20%:", len(noncovid_folder_counts_twenty))

print("Length of COVID-19 Folder Counts 5%:", len(covid_folder_counts_five))
print("Length of Non-COVID Folder Counts 5%:", len(noncovid_folder_counts_five))


######### BY KENAN MORANI
