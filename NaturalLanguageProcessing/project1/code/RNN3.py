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

train_vectors = torch.from_numpy(np.load('w2i/train_vectors.npy'))
valid_vectors = torch.from_numpy(np.load('w2i/valid_vectors.npy'))
test_vectors = torch.from_numpy(np.load('w2i/test_vectors.npy'))
train_labels = torch.from_numpy(np.load('w2i/train_labels.npy'))
valid_labels = torch.from_numpy(np.load('w2i/valid_labels.npy'))
test_labels = torch.from_numpy(np.load('w2i/test_labels.npy'))
weight = torch.from_numpy(np.load('w2i/weight.npy'))

# Hyper Parameters
EPOCH = 10 
BATCH_SIZE = 256
HIDDEN_SIZE = 64
SEQ_LEN = train_vectors.shape[1]
VOCAB_SIZE = weight.shape[0]    
EMBEDDING_DIM = weight.shape[1]
LR = 0.001           

train_data = TensorDataset(train_vectors, train_labels) 
train_loader = DataLoader(dataset=train_data, batch_size=BATCH_SIZE, shuffle=True)
valid_x = valid_vectors
valid_y = valid_labels

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
        self.w_omega = nn.Parameter(torch.Tensor(HIDDEN_SIZE, HIDDEN_SIZE))
        self.u_omega = nn.Parameter(torch.Tensor(HIDDEN_SIZE, 1))
        self.dropout = nn.Dropout(0.5)
        self.out = nn.Linear(HIDDEN_SIZE, 2)
        nn.init.uniform_(self.w_omega, -0.1, 0.1)
        nn.init.uniform_(self.u_omega, -0.1, 0.1)

    def att(self, x):
        u = torch.tanh(torch.matmul(x, self.w_omega))
        att = torch.matmul(u, self.u_omega)
        att_score = F.softmax(att, dim=1)
        scored_x = x * att_score
        feat = torch.sum(scored_x, dim=1) #加权求和
        return feat

    def forward(self, x):
        r = self.word_embed(x)
        r, _ = self.rnn(r)  
        r = self.att(r)
        r = self.dropout(r)
        out = self.out(r)
        return out

rnn = RNN().to(device)
print(rnn)

optimizer = torch.optim.Adam(rnn.parameters(), lr=LR)   # optimize all rnn parameters
loss_func = nn.CrossEntropyLoss()                       
loss_t = []
acc_t = []
acc_v = []
best_acc = 0

for epoch in range(EPOCH):
    for step, (b_x, b_y) in enumerate(train_loader):        # gives batch data
        # train
        rnn.train()           
        b_x = b_x.to(device).long()
        b_y = b_y.to(device).long()
        output = rnn(b_x)    

        loss = loss_func(output, b_y)                   
        loss_t.append(loss.item())
        
        optimizer.zero_grad()   # clear gradients for this training step
        loss.backward()         # backpropagation, compute gradients
        optimizer.step()        # apply gradients
       
        # evaluate
        if step % 118 == 0:
            rnn.eval()
            with torch.no_grad():
                valid_x = valid_x.to(device).long()
                valid_y = valid_y.to(device).long()
                valid_output = rnn(valid_x) 
                valid_loss = loss_func(valid_output, valid_y)  

                pred_train = output.argmax(-1)
                pred_valid = valid_output.argmax(-1)
                train_acc = (pred_train.cpu() == b_y.cpu()).float().mean().data.numpy()
                valid_acc = (pred_valid.cpu() == valid_y.cpu()).float().mean().data.numpy()

            acc_t.append(train_acc)
            acc_v.append(valid_acc)
            
            if valid_acc > best_acc:
                best_acc = valid_acc
                torch.save(rnn.state_dict(), 'RNN3.ckpt')
            print('Epoch: ', epoch, '| train loss: %.4f' % loss.item(), '| train accuracy: %.4f' % train_acc, '| valid loss: %.4f' % valid_loss.item(), '| valid accuracy: %.4f' % valid_acc)
        
# test
rnn.load_state_dict(torch.load('RNN3.ckpt'))
rnn = rnn.to(device)
rnn.eval()
with torch.no_grad():
    test_x = test_vectors.to(device).long()
    test_y = test_labels.to(device).long()
    test_output = rnn(test_x)   
    pred_y = test_output.argmax(-1)   
    acc = (pred_y.cpu() == test_y.cpu()).float().mean().data.numpy()
print('test accuracy: %.4f' % acc)

report = classification_report(pred_y.cpu(), test_y.cpu(), target_names=['1','0'])
print(report)


x1 = [i for i in range(len(loss_t))]
x2 = [i for i in range(len(acc_v))]
plt.plot(x1, loss_t, color='tab:blue', label='train loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')
plt.show()

plt.plot(x2, acc_t, color='tab:blue', label='train accuracy')
plt.plot(x2, acc_v, color='tab:orange', label='valid accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.show()




# %%
