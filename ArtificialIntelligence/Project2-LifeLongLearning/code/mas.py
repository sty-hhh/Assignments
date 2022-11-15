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

os.environ['CUDA_VISIBLE_DEVICES']='1'
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
                 kernel_size_list=(3,4,5),#三个核
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
        x = self.embedding(x.long())
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
        
import tqdm
from tqdm import trange

def train(model, optimizer, dataloader, epochs_per_task, lll_object, lll_lambda, test_dataloaders, evaluate, device):
    model.train()
    model.zero_grad()
    objective = nn.CrossEntropyLoss()
    acc_per_epoch = []
    loss = 1.0
    bar = tqdm.auto.trange(epochs_per_task, leave=False, desc=f"Epoch 1, Loss: {loss:.7f}")
    for epoch in bar:
        # train
        model.train()
        for module in model.modules():
            if isinstance(module, nn.Dropout):
                module.training = True
        for x, y in tqdm.auto.tqdm(dataloader, leave=False):            
            x, y = x.to(device), y.to(device)
            outputs = model(x)
            loss = objective(outputs, y)
            total_loss = loss
            lll_loss = lll_object.penalty(model)
            total_loss += lll_lambda * lll_loss 
            lll_object.update(model)
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()

            loss = total_loss.item()
            bar.set_description_str(desc=f"Epoch {epoch+1:2}, Loss: {loss:.7f}", refresh=True)
        acc_average  = []
        # evaluate
        for test_dataloader in test_dataloaders: 
            acc_test = evaluate(model, test_dataloader, device)
            acc_average.append(acc_test)
        average=np.mean(np.array(acc_average))

        acc_per_epoch.append(average*100.0)
        bar.set_description_str(desc=f"Epoch {epoch+2:2}, Loss: {loss:.7f}", refresh=True)
    return model, optimizer, acc_per_epoch

def evaluate(model, test_dataloader, device):
    model.eval()
    correct_cnt = 0
    total = 0
    for x, labels in test_dataloader:
        x, labels = x.to(device), labels.to(device)
        outputs = model(x)
        _, pred_label = torch.max(outputs.data, 1)
        correct_cnt += (pred_label == labels.data).sum().item()
        total += torch.ones_like(labels.data).sum().item()
    return correct_cnt / total


class mas(object):
    def __init__(self, model: nn.Module, dataloaders: list, device):
        self.model = model 
        self.dataloaders = dataloaders
        self.params = {n: p for n, p in self.model.named_parameters() if p.requires_grad} 
        self.p_old = {} 
        self.device = device
        self._precision_matrices = self.calculate_importance() 
        for n, p in self.params.items():
            self.p_old[n] = p.clone().detach() 
    
    def calculate_importance(self):
        precision_matrices = {}
        for n, p in self.params.items():
            precision_matrices[n] = p.clone().detach().fill_(0) 
        self.model.train()
        for module in self.model.modules():
            if isinstance(module, nn.Dropout):
                module.training = False
        # self.model.eval()
        if self.dataloaders[0] is not None:
            num_data = sum([len(loader) for loader in self.dataloaders])
            for dataloader in self.dataloaders:
                for data in dataloader:
                    self.model.zero_grad()
                    output = self.model(data[0].to(self.device))
                    output.pow_(2)                                                   
                    loss = torch.sum(output,dim=1)  # 不需要label！                          
                    loss = loss.mean()   
                    loss.backward()                                               
                    for n, p in self.model.named_parameters():                      
                        precision_matrices[n].data += p.grad.abs() / num_data                
        precision_matrices = {n: p for n, p in precision_matrices.items()}
        return precision_matrices

    def penalty(self, model: nn.Module):
        loss = 0
        for n, p in model.named_parameters():
            _loss = self._precision_matrices[n] * (p - self.p_old[n]) ** 2
            loss += _loss.sum()
        return loss
    
    def update(self, model):
        return 


# MAS
print("RUN MAS")
model = RNN()
model = model.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

lll_object=mas(model=model, dataloaders=[None],device=device)
lll_lambda=0.1
mas_acc= []
task_bar = tqdm.auto.trange(len(train_dataloaders),desc="Task   1")
for train_indexes in task_bar:
    model, _, acc_list = train(model, optimizer, train_dataloaders[train_indexes], EPOCH, \
        lll_object, lll_lambda, evaluate=evaluate,device=device, test_dataloaders=test_dataloaders[:train_indexes+1])
    lll_object=mas(model=model, dataloaders=test_dataloaders[:train_indexes+1],device=device)
    optimizer = torch.optim.Adam(model.parameters(), LR)
    mas_acc.extend(acc_list)
    task_bar.set_description_str(f"Task  {train_indexes+2:2}")
     
print(mas_acc)
print("==================================================================================================")


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
