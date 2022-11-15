#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define FILE_NAME_LEN 300
#define BUF_LEN 20

typedef struct {
    char fileName[FILE_NAME_LEN];
    __int64 fileSize;
} FileStruct;

char name[FILE_NAME_LEN];
char buf[BUF_LEN];

__int64 getFileSize(char* fileName) {
    FILE* fp;
    if (fopen_s(&fp, fileName, "rb") != NULL) {
        printf("文件打开失败!\n");
        return -1;
    }
    fseek(fp, 0L, SEEK_END);
    int s = ftell(fp);
    fclose(fp);
    return s;
}

void getFileName(char* name) {
    printf("输入目标文件名(含路径):");
    scanf_s("%s", name, FILE_NAME_LEN);
}

int packFile(char* srcFileName, FILE* destFile) {
    FILE* sfile = NULL;
    if (fopen_s(&sfile, name, "rb") != NULL) {
        printf("文件打开失败!\n");
        return 0;
    }
    int len = 0;
    while ((len = fread(buf, 1, BUF_LEN, sfile)) >= BUF_LEN)
        fwrite(buf, 1, BUF_LEN, destFile);
    fwrite(buf, 1, len, destFile);
    fclose(sfile);
    return 1;
}

int main() {
    FILE* dfile = NULL;
    FileStruct f;
    int cnt = 0;
    char srcFileName[FILE_NAME_LEN] = "f:\\test\\filepack.pak";
    getFileName(srcFileName);
    if ((fopen_s(&dfile, srcFileName, "wb")) != NULL) {
        printf("文件打开失败!\n");
        return 0;
    }
    while (true) {
        printf("输入要打包的#%d文件（含路径）：", ++cnt);
        scanf_s("%s", name, FILE_NAME_LEN);
        if (strcmp(name, "exit") == 0) break;
        f.fileSize = getFileSize(name);
        if (f.fileSize == -1) return 0;
        strcpy_s(f.fileName, FILE_NAME_LEN, strrchr(name, '\\') + 1);
        if (fwrite(&f, sizeof(FileStruct), 1, dfile) != 1)
            printf("file write error!\n");
        packFile(srcFileName, dfile);
    }
    printf("打包结束！\n");
    printf("\n");
    printf("按任意键继续...\n");
    fclose(dfile);
    getchar();
    getchar();
    return 0;
}