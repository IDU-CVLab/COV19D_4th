# -*- coding: utf-8 -*-
"""Swin_Transformer_pytorch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kmmVezctjZQYWtl1Qjxdwwq41MUDrOrD
"""

#from google.colab import drive
#drive.mount('/content/gdrive', force_remount=True)

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

import numpy as np
import pandas as pd
import glob
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from sklearn.utils import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import Sequence, to_categorical
import matplotlib.pyplot as plt

# Set device
device = torch.device("cpu")
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Set paths
train_dir = '/home/idu/Desktop/COV19D/train-KD/'
val_dir = '/home/idu/Desktop/COV19D/val-KD/'


# Define hyperparameters
learning_rate = 0.001
num_epochs = 10
batch_size = 32
# Change input images shape to fit the transformer architecture
img_height = 224  
img_width = 224

num_classes = 2

# Define transformations for the images
transform = transforms.Compose([
    transforms.Resize((img_height, img_width)),
    transforms.Grayscale(num_output_channels=1),  # Convert to single-channel grayscale
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])  # Normalize single channel
])

# Load the dataset
train_dataset = datasets.ImageFolder(train_dir, transform=transform)
val_dataset = datasets.ImageFolder(val_dir, transform=transform)

# Create the train and validation data loaders
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

### Choose a Transformer

#### Swin Transformer model
#model = timm.create_model('swin_base_patch4_window12_384', pretrained=True, num_classes=num_classes, in_chans=1)
#model = timm.create_model('swin_tiny', pretrained=True, num_classes=num_classes, in_chans=1)

#### ViT model
model = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=num_classes, in_chans=1)
model = timm.create_model('vit_small_patch16_224', pretrained=True, num_classes=num_classes, in_chans=1)


model.to(device)

# Define the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)


best_val_accuracy = 0.0  # Variable to track the best validation accuracy
best_model_path = '/home/idu/Desktop/COV19D/ChatGPT-saved-models/ViT-model.pt'  # Path to save the best model

num_epochs = 20 # Only for evaluating the model performance

counter = 1
# Train the model
from sklearn.metrics import precision_score, recall_score

for epoch in range(num_epochs):
    print('epoch starts')
    model.train()
    total_loss = 0.0
    total_correct = 0
    for images, labels in train_loader:
        #print('2')
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
        #print('6')
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
    
    #if val_accuracy > best_val_accuracy:
        # Update the best validation accuracy and save the model
    best_val_accuracy = val_accuracy
    torch.save(model.state_dict(), best_model_path)

    print(f"Validation Loss: {avg_val_loss:.4f}, Validation Accuracy: {val_accuracy:.4f}")
    print("Validation Precision:", precision)
    print("Validation Recall:", recall)
    #sys.stdout.flush()
    
# Save the trained model
torch.save(model.state_dict(), "/home/idu/Desktop/COV19D/ChatGPT-saved-models/KnowledgeDistillation-model.pt")

 # save full model including architecture
torch.save(model, "/home/idu/Desktop/COV19D/ChatGPT-saved-models/KnowledgeDistillation-model-full.pt")


###### Loading the model

import torch

# Define the path to the saved model file
model_path = "/home/idu/Desktop/COV19D/ChatGPT-saved-models/KnowledgeDistillation-model-full.pt"

# Create an instance of the model class
#model = model()

# Load the saved model parameters
model= torch.load(model_path)

# Set the model to evaluation mode
model.eval()


### Making Predictions

import os
import numpy as np
import torch
from torchvision import transforms
from PIL import Image

# Define the folder path containing the CT images
folder_path = '/home/idu/Desktop/COV19D/val-KD/non-covid'

covid_predictions = []
noncovid_predictions = []
covid_folder_counts = []
noncovid_folder_counts = []


# Iterate through the image files
for fldr in os.listdir(folder_path):
    sub_folder_path = os.path.join(folder_path, fldr)
    for filee in os.listdir(sub_folder_path):
        file_path = os.path.join(sub_folder_path, filee)

        # Load and preprocess the image
        img = Image.open(file_path)
        img = transform(img)
        img = img.unsqueeze(0)  # Add batch dimension

        # Pass the image through the model to get predictions
        with torch.no_grad():
            output = model(img)

        # Interpret the model's output to make predictions
        _, predicted_class = output.max(1)

        # Append the prediction to the corresponding list
        if predicted_class == 0:
            covid_predictions.append(file_path)
        else:
            noncovid_predictions.append(file_path)
        # Append the count of predicted COVID-19 slices and non-COVID slices for this folder
    if len(covid_predictions) > len(noncovid_predictions):
     covid_folder_counts.append(file_path)
    else:
     noncovid_folder_counts.append(file_path)

    # Create empty lists to store the counts of predicted COVID-19 and non-COVID CT folders
    #covid_folder_counts = []
    #noncovid_folder_counts = []

# Print the lists of CT folder counts (COVID-19 and non-COVID)
print("List of COVID-19 Folder Counts:", covid_folder_counts)
print("List of Non-COVID Folder Counts:", noncovid_folder_counts)

print("Length of COVID-19 Folder Counts:", len(covid_folder_counts))
print("Length of Non-COVID Folder Counts:", len(noncovid_folder_counts))
