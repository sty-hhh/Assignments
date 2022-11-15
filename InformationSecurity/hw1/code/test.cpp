#include <bits/stdc++.h>
using namespace std;

/*英文字母使用频率表table*/
double table[]={0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 
                0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749, 
                0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 
                0.00978, 0.02360, 0.00150,0.01974, 0.00074};

/*用kasiski测试法获取key可能的长度*/
vector<int> Find_same(string cipher) {
    vector<int> distance;
    string p = cipher.substr(0, 3);
    for (int i = 3; i < cipher.length()-3; ++i){
        string tmp = cipher.substr(i, 3);
        if (tmp == p) 
            distance.push_back(i);
    }
    return distance;
}

/*计算最大公约数*/
int gcd (int a, int b) {
    if (b == 0) return a;
    else return gcd(b, a % b);
}

/*计算所选分组的重合指数*/
double IC(string cipher, int start, int len) {
    double result = 0.000;
    int s = 0;
    int n[26] = {0};
    while (start <= cipher.length()) {
        n[cipher[start]-'a']++;
        start += len;
        s++;
    }
    for (int i = 0; i < 26; ++i) {
        if (n[i] <= 1) continue;
        result += (double)(n[i]*(n[i]-1))/(double)((s)*(s-1));
    }
    return result;
}

/*确定密匙key的长度*/
int Get_keyLength(string cipher) {
    int key_length;
    vector<int> distance = Find_same(cipher);
    int m = distance[0];
    for (int i = 0; i < distance.size()-1; ++i) 
        for (int j = i+1; j < distance.size(); ++j) 
            m = min(m, gcd(distance[i], distance[j]));
    for (int i = 1; i <= m; ++i) {
        double sum = 0.000;
        for(int j = 0; j < i; ++j) {
            double temp = IC(cipher, j, i);
            sum += temp;
            cout << temp << " ";
        }
        cout << endl;
        int value = (double)fabs(0.065-(double)(sum/(double)i));
        if (fabs(sum/i - 0.065) < 0.01) 
            key_length = i;
    }
    cout << endl;
    return key_length;
}

/*确定密匙*/
vector<int> Get_key(string cipher, int key_length){
    vector<int> key(key_length, 0);
    map<char, int> mp;
    for (int i = 0; i < key_length; ++i) {
        for (int j = 0; j < 26; ++j) {
            mp.clear();
            double pg = 0.000;
            int sum = 0;
            for (int k = i; k < cipher.length(); k += key_length) {
                char c = (char)((cipher[k] - 'a' + j) % 26 + 'a');
                mp[c]++;
                sum++;
            }
            for (char k = 'a'; k <= 'z'; ++k)
                pg += ((double)mp[k]/(double)sum)*table[k-'a'];
            if (fabs(pg-0.065) < 0.01)
                key[i] = j;
        }
    }   
    return key; 
}

int main(){
    char c[500];
    ifstream inFile("cipher.txt");
    inFile.getline(c, 500);
    inFile.close();
    string cipher = c;

    transform(cipher.begin(), cipher.end(), cipher.begin(), ::tolower);
    int key_length = Get_keyLength(cipher);
    vector<int> key = Get_key(cipher, key_length);

    cout << "key_length: " << key_length << endl << "KEY: ";
    for (int i = 0; i < key_length; ++i)
        cout << (char)((26-key[i])%26+'a');
    cout << endl << "TEXT:" << endl;
    for (int i = 0; i < cipher.length(); ++i)
        cout << (char)((cipher[i]-'a'+key[i%key_length])%26+'a');
    cout << endl;
    return 0;
}