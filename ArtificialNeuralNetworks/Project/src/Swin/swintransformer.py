import os
import csv
import glob
import random

import numpy
import torch
from PIL import Image
# from transformers import AutoFeatureExtractor, SwinModel
from torch import nn
from torchvision.datasets import MNIST
from torch.utils.data import Dataset, DataLoader, ConcatDataset, SubsetRandomSampler, Sampler
from torchvision import transforms, datasets, models
from sklearn.model_selection import KFold
import torch.optim as optim
from torch.optim import lr_scheduler
# from pytorch_pretrained_vit import ViT
import timm
from torch.utils.tensorboard import SummaryWriter   
from tqdm import trange
# from transformers import AutoFeatureExtractor, SwinForImageClassification
from cutmix.cutmix import CutMix
from cutmix.utils import CutMixCrossEntropyLoss

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
k_folds = 5
num_epochs = 50
data_dir = 'skin40Out'
resize1 = 384
resize2 = int(256/224*384)
load_path = './model.pth'
data_transforms_train = transforms.Compose([
    lambda x: Image.open(x).convert("RGB"),
    # transforms.Resize(256),
    # transforms.CenterCrop(224),
    transforms.RandomAffine(degrees=30),
    transforms.RandomResizedCrop(resize1),
    transforms.RandomHorizontalFlip(p=0.5),
    # transforms.RandomRotation(5),
    # transforms.ColorJitter(brightness=0.1, contrast=0.1, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.6075, 0.4912, 0.4606], [
        0.2260, 0.2162, 0.2190])
])
data_transforms_test = transforms.Compose([
    lambda x: Image.open(x).convert("RGB"),
    transforms.Resize(resize2),
    transforms.CenterCrop(resize1),
    transforms.ToTensor(),
    transforms.Normalize([0.6075, 0.4912, 0.4606], [0.2260, 0.2162, 0.2190])
])

writer = SummaryWriter('./path/to/log')


def reset_weights(m):
    """
      Try resetting model weights to avoid
      weight leakage.
    """
    for layer in m.children():
        if hasattr(layer, 'reset_parameters'):
            print(f'Reset trainable parameters of layer = {layer}')
            layer.reset_parameters()


class Skin40(Dataset):

    def __init__(self, root, mode, time, n_augment=2):

        super(Skin40, self).__init__()
        self.root = root
        self.mode = mode
        self.name2label = {}
        self.n_augment = min(n_augment , 4)
        # 返回指定目录下的文件列表，并对文件列表进行排序，
        # os.listdir每次返回目录下的文件列表顺序会不一致，
        # 排序是为了每次返回文件列表顺序一致
        for name in sorted(os.listdir(os.path.join(root))):
            # 过滤掉非目录文件
            if not os.path.isdir(os.path.join(root, name)):
                continue
            # 构建字典，名字：0~4数字
            self.name2label[name] = len(self.name2label.keys())

        # eg: {'squirtle': 4, 'bulbasaur': 0, 'pikachu': 3, 'mewtwo': 2, 'charmander': 1}
        # print(self.name2label)

        # image, label
        temp_images, temp_labels = self.load_csv("images.csv")
        if self.mode == 'train':
            self.images = [content for index, content in enumerate(
                temp_images) if index % k_folds != time]
            self.labels = [content for index, content in enumerate(
                temp_labels) if index % k_folds != time]
        else:
            self.images = [content for index, content in enumerate(
                temp_images) if index % k_folds == time]
            self.labels = [content for index, content in enumerate(
                temp_labels) if index % k_folds == time]

    # 将目录下的图片路径与其对应的标签写入csv文件，
    # 并将csv文件写入的内容读出，返回图片名与其标签
    def load_csv(self, filename):
        """
        :param filename:
        :return:
        """
        # 是否已经存在了cvs文件
        if not os.path.exists(os.path.join(self.root, filename)):
            images = []
            for name in self.name2label.keys():
                # 获取指定目录下所有的满足后缀的图像名
                # Skin40/mewtwo/00001.png
                images += glob.glob(os.path.join(self.root, name, "*.png"))
                images += glob.glob(os.path.join(self.root, name, "*.jpg"))
                images += glob.glob(os.path.join(self.root, name, "*.jpeg"))

            # 将元素打乱
            random.shuffle(images)
            with open(os.path.join(self.root, filename), mode="w", newline="") as f:
                writer = csv.writer(f)
                for img in images:
                    name = img.split(os.sep)[-2]
                    label = self.name2label[name]
                    # 将图片路径以及对应的标签写入到csv文件中
                    writer.writerow([img, label])
                print("writen into csv file: ", filename)

        # 如果已经存在了csv文件，则读取csv文件
        images, labels = [], []
        with open(os.path.join(self.root, filename)) as f:
            reader = csv.reader(f)
            for row in reader:
                # 'Skin40/pikachu/00000058.png', 0
                img, label = row
                label = int(label)

                images.append(img)
                labels.append(label)
        assert len(images) == len(labels)

        return images, labels

    def __len__(self):
        if self.mode == 'train':
            return len(self.images)*self.n_augment
        else:
            return len(self.images)
        # return len(self.images)

    def __getitem__(self, idx):
        # idx~[0~len(images)]
        # self.images, self.labels
        # label: 0
        idx %= len(self.images)
        img, label = self.images[idx], self.labels[idx]
        if self.mode == 'train':
            img = data_transforms_train(img)
        else:
            img = data_transforms_test(img)

        label = torch.tensor(label)

        return img, label


if __name__ == '__main__':

    loss_function = nn.CrossEntropyLoss()

    # For fold results
    results = {}

    # Set fixed random number seed
    torch.manual_seed(3407)

    # Start print
    print('--------------------------------')

    # K-fold Cross Validation model evaluation
    for fold in range(k_folds):

        # Print
        print(f'FOLD {fold}')
        print('--------------------------------')
        # train_ids.transforms = data_transforms_train
        # Sample elements randomly from a given list of ids, no replacement.

        training_set = Skin40(data_dir, 'train', fold, 3)
        training_set = CutMix(training_set, num_class=40, beta=1.0, prob=0.5, num_mix=2)
        loss_function = CutMixCrossEntropyLoss(True)

        test_set = Skin40(data_dir, 'test', fold, 3)

        # Define data loaders for training and testing data in this fold
        trainloader = torch.utils.data.DataLoader(
            training_set,
            batch_size=16, shuffle=True, num_workers=os.cpu_count())
        testloader = torch.utils.data.DataLoader(
            test_set,
            batch_size=16, shuffle=True, num_workers=os.cpu_count())

        # Init the neural network
        # network = models.densenet161(pretrained=True)
        # num_ftrs = network.classifier.in_features
        # # # network = models.resnet101(pretrained=True)
        # network.classifier = nn.Linear(num_ftrs, 40)
        network = timm.create_model('swin_large_patch4_window12_384', pretrained=True, num_classes=40)

        # network = ViT('L_16_imagenet1k', pretrained=True)
        # network = SwinModel.from_pretrained("microsoft/swin-base-patch4-window12-384-in22k")

        # parameters = model.classifier.parameters()
        # num_ftrs = network.fc.in_features
        # # Here the size of each output sample is set to 2.
        # # Alternatively, it can be generalized to nn.Linear(num_ftrs, len(class_names)).
        # network.fc = nn.Linear(num_ftrs, 40)
        # network.load_state_dict(torch.load(load_path))
        # num_ftrs = network.fc.in_features
        # network.fc = nn.Linear(num_ftrs, 40)

        network = network.to(device)
        # Initialize optimizer
        # Observe that all parameters are being optimized
        # optimizer = optim.SGD(network.parameters(), lr=0.001, momentum=0.9)
        optimizer = torch.optim.AdamW(network.parameters(),lr=1e-4, weight_decay=1e-3)
        schedulr = torch.optim.lr_scheduler.StepLR(optimizer , step_size = 1 , gamma = 0.88)
        # Decay LR by a factor of 0.1 every 7 epochs
        # scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
        # optimizer = torch.optim.Adam(network.parameters(), lr=1e-4)

        best_acc = 0.0
        save_path = f'./model-fold-{fold}.pth'

        # Run the training loop for defined number of epochs
        for epoch in trange(0, num_epochs):

            # Print epoch
            # print(f'Starting epoch {epoch + 1}')

            # Set current loss value
            # current_loss = 0.0
            running_loss = 0.0
            running_corrects = 0
            train_total = 0

            # Iterate over the DataLoader for training data
            for i, data in enumerate(trainloader, 0):
                # Get inputs
                inputs, targets = data

                inputs = inputs.to(device)
                targets = targets.to(device)

                # Zero the gradients
                optimizer.zero_grad()

                # Perform forward pass
                outputs = network(inputs)

                # Compute loss
                loss = loss_function(outputs, targets)

                # Perform backward pass
                loss.backward()

                # Perform optimization
                optimizer.step()

                _, preds = torch.max(outputs, 1)

                # Print statistics
                running_loss += loss.item() * inputs.size(0)
                train_total += targets.size(0)

            epoch_loss = running_loss / train_total
            # print(f'Loss: {epoch_loss:.4f}')
            writer.add_scalar('epoch_loss', epoch_loss, epoch)
            schedulr.step()

            correct, total = 0, 0
            with torch.no_grad():

                # Iterate over the test data and generate predictions
                for i, data in enumerate(testloader, 0):
                    # Get inputs
                    inputs, targets = data
                    inputs = inputs.to(device)
                    targets = targets.to(device)

                    # Generate outputs
                    outputs = network(inputs)

                    # Set total and correct
                    _, predicted = torch.max(outputs.data, 1)
                    total += targets.size(0)
                    correct += (predicted == targets).sum().item()

                # Print accuracy
                # print('Accuracy: %.4f %%' %
                #       (100.0 * float(correct / total)))
                # print('--------------------------------')
                temp = 100.0 * float(correct / total)

                writer.add_scalar('accuracy', temp, epoch) 

                if temp > best_acc:
                    best_acc = temp
                    torch.save(network.state_dict(), save_path)
                    # print('Best & Save')

        results[fold] = best_acc
        writer.add_scalar('fold', best_acc, fold)

        # # Saving the model
        # save_path = f'./model-fold-{fold}.pth'
        # torch.save(network.state_dict(), save_path)
        # network.load_state_dict(torch.load(save_path))
        # Evaluationfor this fold

    # Print fold results
    print(f'K-FOLD CROSS VALIDATION RESULTS FOR {k_folds} FOLDS')
    print('--------------------------------')
    sum = 0.0
    for key, value in results.items():
        print(f'Fold {key}: {value} %')
        sum += value
    print(f'Average: {sum / len(results.items())} %')
