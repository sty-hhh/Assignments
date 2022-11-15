#%%
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np
import os

# get device 
def get_device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'

os.environ['CUDA_VISIBLE_DEVICES']='0'
device = get_device()
print(f'DEVICE: {torch.cuda.get_device_name()}')

train_data1 = torch.from_numpy(np.load('w2i/train_data1.npy'))
test_data1 = torch.from_numpy(np.load('w2i/test_data1.npy'))
train_label1 = torch.from_numpy(np.load('w2i/train_label1.npy'))
test_label1 = torch.from_numpy(np.load('w2i/test_label1.npy'))

train_data2 = torch.from_numpy(np.load('w2i/train_data2.npy'))
test_data2 = torch.from_numpy(np.load('w2i/test_data2.npy'))
train_label2 = torch.from_numpy(np.load('w2i/train_label2.npy'))
test_label2 = torch.from_numpy(np.load('w2i/test_label2.npy'))

train_data3 = torch.from_numpy(np.load('w2i/train_data3.npy'))
test_data3 = torch.from_numpy(np.load('w2i/test_data3.npy'))
train_label3 = torch.from_numpy(np.load('w2i/train_label3.npy'))
test_label3 = torch.from_numpy(np.load('w2i/test_label3.npy'))

train_data4 = torch.from_numpy(np.load('w2i/train_data4.npy'))
test_data4 = torch.from_numpy(np.load('w2i/test_data4.npy'))
train_label4 = torch.from_numpy(np.load('w2i/train_label4.npy'))
test_label4 = torch.from_numpy(np.load('w2i/test_label4.npy'))

weight = torch.from_numpy(np.load('w2i/weight.npy'))

# Hyper Parameters
EPOCH = 35
BATCH_SIZE = 256
HIDDEN_SIZE = 64 
EMBEDDING_DIM = weight.shape[1]
LR = 0.001           

train1 = TensorDataset(train_data1, train_label1) 
train2 = TensorDataset(train_data2, train_label2) 
train3 = TensorDataset(train_data3, train_label3) 
train4 = TensorDataset(train_data4, train_label4) 
test1 = TensorDataset(test_data1, test_label1) 
test2 = TensorDataset(test_data2, test_label2) 
test3 = TensorDataset(test_data3, test_label3) 
test4 = TensorDataset(test_data4, test_label4) 

train_dataloaders = [
    DataLoader(train1, batch_size=BATCH_SIZE, shuffle=True),
    DataLoader(train2, batch_size=BATCH_SIZE, shuffle=True),
    DataLoader(train3, batch_size=BATCH_SIZE, shuffle=True),
    DataLoader(train4, batch_size=BATCH_SIZE, shuffle=True)
]

test_dataloaders = [
    DataLoader(test1, batch_size=len(test1), shuffle=True),
    DataLoader(test2, batch_size=len(test2), shuffle=True),
    DataLoader(test3, batch_size=len(test3), shuffle=True),
    DataLoader(test4, batch_size=len(test4), shuffle=True)
]

class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()
        # self.word_embed = nn.Embedding(20393,50)
        self.word_embed = nn.Embedding.from_pretrained(weight)
        self.word_embed.weight.requires_grad = True
        self.rnn = nn.LSTM(        
            input_size = EMBEDDING_DIM,
            hidden_size = HIDDEN_SIZE,        
            num_layers = 1,         
            batch_first = True,  
        )
        self.dropout = nn.Dropout(0.5)
        self.out = nn.Linear(HIDDEN_SIZE, 4)

    def forward(self, x):
        r = self.word_embed(x.long())
        r, _ = self.rnn(r)  
        r = self.dropout(r)
        out = self.out(r[:, -1, :])
        return out

class TextCNN(nn.Module):
    def __init__(self,
                 class_num=4,
                 kernel_num=128,
                 kernel_size_list=(3,4,5), 
                 dropout=0.5,embed_dim=300):
        
        super(TextCNN, self).__init__()
        self.embedding = nn.Embedding.from_pretrained(weight)
        self.embedding.weight.requires_grad = True

        self.conv1d_list = nn.ModuleList([
            nn.Conv1d(embed_dim, kernel_num, kernel_size)
                for kernel_size in kernel_size_list#卷积层
        ])
        
        self.linear = nn.Linear(kernel_num * len(kernel_size_list), class_num)#全连接层
        self.dropout = nn.Dropout(dropout)#防止过拟合
        
    def forward(self, x):
        # x的形状为(batch, word_nums)
        # 经过嵌入层之后x的形状为(batch, word_nums, embed_dim)
        x = self.embedding(x)
        
        #因为conv1d的输入需要为: (batch, in_channels, in_length)
        # in_channels是embed_dim, in_length是word_nums
        # 需要将x转换为: (batch, embed_dim, word_nums)
        x = x.transpose(1, 2)
        
        # 经过conv1d之后，(batch, kernel_num, out_length)
        # out_length = word_nums - kernel_size + 1
        x = [F.relu(conv1d(x)) for conv1d in self.conv1d_list]

        # pooling作用在第3维, 窗口大小为第三维的大小
        # 在池化之后变为(batch, kernel_num, 1)
        # squeeze(2)删除第3维
        x = [F.max_pool1d(i, i.shape[2]).squeeze(2) for i in x]

        # shape: (batch, kernel_num * len(kernel_size_list))
        x = torch.cat(x, dim=1)
        x = self.dropout(x)
        # shape: (batch, class_num)
        x = self.linear(x)
        return x

#model = RNN().to(device)
model = TextCNN().to(device)
print(model)

optimizer = torch.optim.Adam(model.parameters(), lr=LR)   # optimize all rnn parameters
loss_func = nn.CrossEntropyLoss()                       
loss_t = []
acc_t = []
acc_v = []
best_acc = 0

def evaluate(model, test_dataloader, device):
    model.eval()
    correct_cnt = 0
    total = 0
    for imgs, labels in test_dataloader:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs = model(imgs)
        _, pred_label = torch.max(outputs.data, 1)

        correct_cnt += (pred_label == labels.data).sum().item()
        total += torch.ones_like(labels.data).sum().item()
    return correct_cnt / total

# train
for epoch in range(EPOCH):
    for step, (b_x, b_y) in enumerate(train_dataloaders[0]):        # gives batch data
        # train
        model.train()           
        b_x = b_x.to(device)
        b_y = b_y.to(device)
        output = model(b_x)    

        loss = loss_func(output, b_y)                   
        loss_t.append(loss.item())
        
        optimizer.zero_grad()   # clear gradients for this training step
        loss.backward()         # backpropagation, compute gradients
        optimizer.step()        # apply gradients
    acc = evaluate(model, test_dataloaders[0], device)
    print('Epoch:',epoch,'Acc:',acc)
       


acc = []
sss = 0
for i in range(4):
    temp = evaluate(model, test_dataloaders[i], device)
    acc.append(temp)
    sss += temp * len(test_dataloaders[i])
sss /= (len(test_dataloaders[0])+len(test_dataloaders[1])+len(test_dataloaders[2])+len(test_dataloaders[3]))
print(acc)
print(sss)

# %%
