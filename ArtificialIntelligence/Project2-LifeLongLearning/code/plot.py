# %%
#Load the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




# 5个点
N = 5
x1 = [i for i in range(5)]  # baseline
x2 = [i+5 for i in range(5)] # ewc
x3 = [i+10 for i in range(5)] # mas
x4 = [i+15 for i in range(5)] # si
x5 = [i+20 for i in range(5)] # 单模型

y1_rnn_comp = [0.5851,0.6030,0.5441,0.6427,0.5710]
y2_rnn_comp = [0.6568,0.6619,0.5975,0.6530,0.6914]
y3_rnn_comp = [0.6811,0.6555,0.6933,0.7451,0.6274]
y4_rnn_comp = [0.6389,0.6376,0.6542,0.6517,0.5979]
y5_rnn_comp = [0.7810,0.7720,0.7618,0.8020,0.7861]

plt.scatter(x1, y1_rnn_comp, marker='o', color="red")
plt.scatter(x2, y2_rnn_comp, marker='o', color="blue")
plt.scatter(x3, y3_rnn_comp, marker='o', color="green")
plt.scatter(x4, y4_rnn_comp, marker='o', color="brown")
plt.scatter(x5, y5_rnn_comp, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of RNN in comp')
plt.show()

y1_cnn_comp = [0.7179,0.7093,0.7157,0.7247,0.7157]
y2_cnn_comp = [0.7016,0.6965,0.6952,0.7067,0.7208]
y3_cnn_comp = [0.7349,0.7439,0.7351,0.7451,0.7347]
y4_cnn_comp = [0.7439,0.7298,0.7299,0.7349,0.7413]
y5_cnn_comp = [0.8233,0.8130,0.8220,0.8284,0.8285]

plt.scatter(x1, y1_cnn_comp, marker='o', color="red")
plt.scatter(x2, y2_cnn_comp, marker='o', color="blue")
plt.scatter(x3, y3_cnn_comp, marker='o', color="green")
plt.scatter(x4, y4_cnn_comp, marker='o', color="brown")
plt.scatter(x5, y5_cnn_comp, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of CNN in comp')
plt.show()

y1_rnn_rec = [0.8592,0.7851,0.7525,0.7587,0.7889]
y2_rnn_rec = [0.8618,0.7952,0.8517,0.8140,0.8505]
y3_rnn_rec = [0.8479,0.8706,0.8216,0.8618,0.8153]
y4_rnn_rec = [0.8454,0.8040,0.8479,0.8567,0.8643]
y5_rnn_rec = [0.9271,0.9309,0.9170,0.9283,0.9409]

plt.scatter(x1, y1_rnn_rec, marker='o', color="red")
plt.scatter(x2, y2_rnn_rec, marker='o', color="blue")
plt.scatter(x3, y3_rnn_rec, marker='o', color="green")
plt.scatter(x4, y4_rnn_rec, marker='o', color="brown")
plt.scatter(x5, y5_rnn_rec, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of RNN in rec')
plt.show()

y1_cnn_rec = [0.8643,0.8693,0.8567,0.8592,0.8680]
y2_cnn_rec = [0.8806,0.8856,0.8781,0.8768,0.8769]
y3_cnn_rec = [0.9045,0.8856,0.8982,0.8969,0.8957]
y4_cnn_rec = [0.8894,0.8969,0.8944,0.8881,0.8982]
y5_cnn_rec = [0.9522,0.9523,0.9521,0.9510,0.9472]

plt.scatter(x1, y1_cnn_rec, marker='o', color="red")
plt.scatter(x2, y2_cnn_rec, marker='o', color="blue")
plt.scatter(x3, y3_cnn_rec, marker='o', color="green")
plt.scatter(x4, y4_cnn_rec, marker='o', color="brown")
plt.scatter(x5, y5_cnn_rec, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of CNN in rec')
plt.show()

y1_rnn_sci = [0.7386,0.7032,0.7108,0.7297,0.6351]
y2_rnn_sci = [0.6540,0.6919,0.7095,0.7348,0.7108]
y3_rnn_sci = [0.7196,0.7398,0.7196,0.6893,0.6515]
y4_rnn_sci = [0.6893,0.6641,0.7335,0.7209,0.7310]
y5_rnn_sci = [0.7512,0.7891,0.7840,0.7929,0.8219]

plt.scatter(x1, y1_rnn_sci, marker='o', color="red")
plt.scatter(x2, y2_rnn_sci, marker='o', color="blue")
plt.scatter(x3, y3_rnn_sci, marker='o', color="green")
plt.scatter(x4, y4_rnn_sci, marker='o', color="brown")
plt.scatter(x5, y5_rnn_sci, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of RNN in sci')
plt.show()

y1_cnn_sci = [0.7929,0.7916,0.7828,0.8005,0.7916]
y2_cnn_sci = [0.8017,0.8042,0.7941,0.7929,0.7945]
y3_cnn_sci = [0.7967,0.8050,0.7992,0.8055,0.8106]
y4_cnn_sci = [0.7961,0.7992,0.8017,0.7954,0.8080]
y5_cnn_sci = [0.8788,0.8712,0.8787,0.8750,0.8762]

plt.scatter(x1, y1_cnn_sci, marker='o', color="red")
plt.scatter(x2, y2_cnn_sci, marker='o', color="blue")
plt.scatter(x3, y3_cnn_sci, marker='o', color="green")
plt.scatter(x4, y4_cnn_sci, marker='o', color="brown")
plt.scatter(x5, y5_cnn_sci, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of CNN in sci')
plt.show()

y1_rnn_talk = [0.8525,0.8233,0.8279,0.8248,0.8371]
y2_rnn_talk = [0.8172,0.7788,0.7987,0.8218,0.7818]
y3_rnn_talk = [0.8463,0.8110,0.8095,0.8079,0.7788]
y4_rnn_talk = [0.7649,0.7050,0.7757,0.8018,0.8019]
y5_rnn_talk = [0.8433,0.8110,0.8371,0.8233,0.8341]

plt.scatter(x1, y1_rnn_talk, marker='o', color="red")
plt.scatter(x2, y2_rnn_talk, marker='o', color="blue")
plt.scatter(x3, y3_rnn_talk, marker='o', color="green")
plt.scatter(x4, y4_rnn_talk, marker='o', color="brown")
plt.scatter(x5, y5_rnn_talk, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of RNN in talk')
plt.show()

y1_cnn_talk = [0.8556,0.8525,0.8617,0.8479,0.8586]
y2_cnn_talk = [0.8586,0.8540,0.8463,0.8496,0.8543]
y3_cnn_talk = [0.8663,0.8479,0.8540,0.8586,0.8540]
y4_cnn_talk = [0.8505,0.8479,0.8479,0.8325,0.8356]
y5_cnn_talk = [0.8709,0.8678,0.8755,0.8694,0.8678]

plt.scatter(x1, y1_cnn_talk, marker='o', color="red")
plt.scatter(x2, y2_cnn_talk, marker='o', color="blue")
plt.scatter(x3, y3_cnn_talk, marker='o', color="green")
plt.scatter(x4, y4_cnn_talk, marker='o', color="brown")
plt.scatter(x5, y5_cnn_talk, marker='o', color="orange")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of CNN in talk')
plt.show()

y1_rnn_ave = [0.7526,0.7224,0.7009,0.7337,0.6994]
y2_rnn_ave = [0.7474,0.7319,0.7395,0.7559,0.7586]
y3_rnn_ave = [0.7738,0.7692,0.7610,0.7760,0.7182]
y4_rnn_ave = [0.7346,0.7027,0.7528,0.7578,0.7487]

plt.scatter(x1, y1_rnn_ave, marker='o', color="red")
plt.scatter(x2, y2_rnn_ave, marker='o', color="blue")
plt.scatter(x3, y3_rnn_ave, marker='o', color="green")
plt.scatter(x4, y4_rnn_ave, marker='o', color="brown")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of RNN in average')
plt.show()

y1_cnn_ave = [0.8042,0.8026,0.8004,0.8054,0.8052]
y2_cnn_ave = [0.8106,0.8101,0.8034,0.8065,0.8115]
y3_cnn_ave = [0.8256,0.8195,0.8216,0.8266,0.8238]
y4_cnn_ave = [0.8202,0.8184,0.8185,0.8127,0.8208]

plt.scatter(x1, y1_cnn_ave, marker='o', color="red")
plt.scatter(x2, y2_cnn_ave, marker='o', color="blue")
plt.scatter(x3, y3_cnn_ave, marker='o', color="green")
plt.scatter(x4, y4_cnn_ave, marker='o', color="brown")
plt.legend(['baseline','ewc','mas','si','single'])
plt.xlabel('Methods')
plt.ylabel('Accuracy')
plt.title('Accuracy of CNN in average')
plt.show()








# %%
