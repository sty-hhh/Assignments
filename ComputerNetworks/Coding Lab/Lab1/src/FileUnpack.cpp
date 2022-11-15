#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define FILE_NAME_LEN 300
#define BUF_LEN 20
#define HASH_SIZE 19260817

typedef struct {
    char fileName[FILE_NAME_LEN];
    __int64 fileSize;
} FileStruct;

int HashFunc(char* str) {
    int s = 131, hash = 0;
    while (*str)
        hash = hash * s + (*str++);
    return (hash & 0x7FFFFFFF) % HASH_SIZE;
}

char ans[BUF_LEN];
char* div(char* filePathName) {
    memset(ans, '\0', sizeof(ans));
    char* p = strrchr(filePathName, '.');
    for (int i = 0; i < strlen(filePathName) - strlen(p); ++i) 
        ans[i] = filePathName[i];
    return ans;
}

int cnt[HASH_SIZE] = { 0 };
int unpackFile(FILE* sfile, char* Path) {
    FILE* dfile = NULL;
    FileStruct f;
    while (fread(&f, sizeof(FileStruct), 1, sfile) == 1) {
        char temp[BUF_LEN];
        char part[BUF_LEN] = "(0)";
        strcpy_s(temp, FILE_NAME_LEN, Path);
        strcat_s(temp, FILE_NAME_LEN, "\\");
        strcat_s(temp, FILE_NAME_LEN, div(f.fileName));
        int res = HashFunc(f.fileName);
        if (cnt[res]++) {
            part[1] += cnt[res];
            strcat_s(temp, FILE_NAME_LEN, part);
        }
        strcat_s(temp, FILE_NAME_LEN, strrchr(f.fileName, '.'));
        if (fopen_s(&dfile, temp, "wb") != NULL) {
            printf("文件解包失败！\n");
            getchar();
            getchar();
            return 0;
        }
        int left = f.fileSize;
        char buf[BUF_LEN];
        while (left) {
            int Size = left > BUF_LEN ? BUF_LEN : left;
            fread(buf, Size, 1, sfile);
            fwrite(buf, Size, 1, dfile);
            left -= Size;
        }
    }
    fclose(dfile);
}

int main() {
    FILE* sfile = NULL;
    char dic[FILE_NAME_LEN];
    char name[FILE_NAME_LEN];
    printf("输入目标文件夹：");
    scanf_s("%s", dic, FILE_NAME_LEN);
    printf("输入要解包的文件：");
    scanf_s("%s", name, FILE_NAME_LEN);
    if (fopen_s(&sfile, name, "rb") != NULL) {
        printf("文件打开失败！\n");
        getchar();
        getchar();
        return 0;
    }
    unpackFile(sfile, dic);
    printf("解包结束！\n");
    fclose(sfile);
    getchar();
    getchar();
    return 0;
}