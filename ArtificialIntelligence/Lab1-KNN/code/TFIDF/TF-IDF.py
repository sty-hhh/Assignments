import math

# 读取文件
def read_file():
    data = []
    with open("semeval.txt", "r") as f:
        total = len(f.readlines())      # 统计行数
        f.seek(0, 0)                    # 文件指针复位
        for sentence in f:
            # 拆分每一行并将第三个部分的句子赋值给sentence，取[0:-1]是为了把句末的回车符去掉
            data.append(sentence.split('\t')[2][0:-1])
    return data, total

# 构建词表
def count_words(data):
    word_list = []
    for sentence in data:
        words =  sentence.split(' ')    # 将每一行用空格划分为多个单词
        for word in words:
            if word not in word_list: 
                word_list.append(word)  # 如果单词不在词表中，则将单词加入词表
    return word_list

# 计算TF矩阵，求出TF矩阵的一行
def TF(words):
    tf = {}
    num = len(words)    # 计算一行中的单词个数
    for word in words:
        tf[word] = (tf.get(word, 0)*num+1)/num  # 按照公式计算TF
    return tf

# 计算IDF的值
def IDF(data, word_list):
    idf = []
    for word in word_list:  # 遍历词表中的每个词
        count = 0
        for sentence in data:
            words =  sentence.split(' ')    # 将每一行用空格划分为多个单词
            if word in words: 
                count += 1  # 如果该单词在这一行中，计数器count加上1
        idf.append(math.log(total/(count+1)))   # 利用公式计算
    return idf

# 输出到文件
def write_file(tfidf):
    with open("19335174_ShiTianyu_TFIDF.txt", "w") as f:
        for line in tfidf:
            for x in line:
                if x != 0:  # 如果值不为0，输出该值
                    f.write(str(x))
                    f.write(' ')
            f.write('\n')

# 主函数
if __name__ ==  '__main__':
    data, total = read_file()       # data是从文件读入的数据，total是总行数
    word_list = count_words(data)   # 由data构建词表word_list
    idf = IDF(data, word_list)      # 计算idf的值
    tfidf = []
    for sentence in data:
        words = sentence.split(' ')
        tf = TF(words)              # 计算每一行的tf的值
        line = []
        index = 0
        for word in word_list:
            x = tf.get(word, 0)*idf[index]  # 利用公式计算tf-idf
            line.append(x)                  # 在该行中添加一个值
            index += 1                      # idf的索引加1
        tfidf.append(line)          # tfidf矩阵添加一行
    write_file(tfidf)           # 输出到文件
