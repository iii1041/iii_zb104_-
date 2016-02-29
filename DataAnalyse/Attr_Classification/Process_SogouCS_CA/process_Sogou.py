# -*- coding: utf-8 -*-
#######################
#process_Sogou.py

#功能
#將Sogou的原始語料轉換成word2vec能用的txt檔
#適用於SogouCS . SogouCA 兩種資料

#前置作業

#需要檔案 : (放在同義層)
#1. 字典.停用詞
#2. 一存放N個TXT檔的語料庫資料夾(SogouCS / SogouCA)
#3. 此程式(process_Sogou.py)
#4. 訓練程式(train_word2vec_model.py)

#確認有字典 & 停用詞，程式採用以下資源，可自我修改
#'dict.big.tra.txt'  #預設字典
#'dict_twstd_tfidf.txt'  #中文分詞詞庫(TFIDF)
#'dict_ntusd_pos.txt' #NTUSD_負向
#'dict_ntusd_nag.txt' #NTUSD_正向
#'dict_twedu_dict.txt' #教育部《重編國語辭典 修訂本》
#"stopwords_1218_OriForSougo.txt" #停用詞

#步驟：
#1.使用ConvertZ將檔案轉為UTF-8
#2.使用OpenCC將檔案轉為台灣繁體(常用詞)  --> 並放進資料夾 EX: 'SogouCSTest'
#3.在命令列執行 'python process_Sogou.py [資料夾名稱]'
#-->EX: 'python process_Sogou.py SogouCSTest'

#4.使用完畢即可得到一堆資料夾跟一個TXT檔，TXT檔的名稱-->[資料夾名稱]_5_Combine.txt
#5.使用train_word2vec_model.py，訓練word2Vec模型
#-->在命令列執行 'python train_word2vec_model.py [資料夾名稱]_5_Combine.txt [資料夾名稱]_5_Combine.model [資料夾名稱]_5_Combine.vector'

#######################
import sys
import time
import os
import jieba
import jieba.analyse
import jieba.posseg as pseg
from bs4 import BeautifulSoup as bs

#目標資料夾
##################
Dir = sys.argv[1]
##################


#V2__把Content的內容取出來
a = time.time()

os.popen('mkdir '+Dir+'_2') #建立'二版'資料夾
for name in os.listdir(Dir): #從一版資料夾讀出
    From = Dir + '//' + name
    target = Dir+'_2'+'//' + name
    with open(target,'w') as fid:
        with open(From, 'r') as f:
            soup = bs(f.read(),"lxml")
            for i in soup.select('content'): #取出content內容
                fid.write(i.text.encode('utf-8')) #編碼寫進檔案
                fid.write('\n')

#V3__把全形英數字取代成半形
b = time.time()
print 'V2_Done!_Cost:',(b-a)

Dic = {'Ａ':'A','Ｂ':'B','Ｃ':'C','Ｄ':'D','Ｅ':'E','Ｆ':'F','Ｇ':'G','Ｈ':'H','Ｉ':'I','Ｊ':'J','Ｋ':'K','Ｌ':'L','Ｍ':'M','Ｎ':'N','Ｏ':'O','Ｐ':'P','Ｑ':'Q',\
'Ｒ':'R','Ｓ':'S','Ｔ':'T','Ｕ':'U','Ｖ':'V','Ｗ':'W','Ｘ':'X','Ｙ':'Y','Ｚ':'Z','ａ':'a','ｂ':'b','ｃ':'c','ｄ':'d','ｅ':'e','ｆ':'f','ｇ':'g','ｈ':'h','ｉ':'i','ｊ':'j',\
'ｋ':'k','ｌ':'l','ｍ':'m','ｎ':'n','ｏ':'o','ｐ':'p','ｑ':'q','ｒ':'r','ｓ':'s','ｔ':'t','ｕ':'u','ｖ':'v','ｗ':'w','ｘ':'x','ｙ':'y','ｚ':'z','１':'1','２':'2','３':'3',\
'４':'4','５':'5','６':'6','７':'7','８':'8','９':'9','０':'0','．':'.'}

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

os.popen('mkdir '+Dir+'_3') #建立'三版'資料夾
for name in os.listdir(Dir+'_2'): #從二版資料夾讀出
    From = Dir + '_2' + '//' + name
    target = Dir+'_3' + '//' + name
    with open(target,'w') as f2:
        for o in open(From,'r'): #讀出每一行
            f2.write((replace_all(o.strip(),Dic))+'\n') #全半形取代


#V4__斷詞
c = time.time()
print 'V3_Done!_Cost:',(c-b)

jieba.set_dictionary('dict.big.tra.txt')  #預設字典
jieba.load_userdict('dict_twstd_tfidf.txt')  #中文分詞詞庫(TFIDF)
jieba.load_userdict('dict_ntusd_pos.txt') #NTUSD_負向
jieba.load_userdict('dict_ntusd_nag.txt') #NTUSD_正向
jieba.load_userdict('dict_twedu_dict.txt') #教育部《重編國語辭典 修訂本》
jieba.analyse.set_stop_words("stopwords_1218_OriForSougo.txt") #停用詞

dot = {'。','（','）','！','「','」','，','、','；','：','”','“','～',\
        '＜','＞','．','é','︶','『','』','﹗','ī','ō','／',"〔", '〕','｜',\
        "？","＠","｛","｝","￥","《","》",'…','【','】','︿','＃','＄','％','＆','＊','＋','⊙','［','］',\
       "［","］","—","·","－"}

os.popen('mkdir '+Dir+'_4') #建立'四版'資料夾
for name in os.listdir(Dir+'_3'): #從三版資料夾讀出
    In = Dir+'_3'+'//' + name
    Out = Dir+'_4'+'//' + name
    with open(Out,'w') as w:
        for o in open(In,'r'):
            Cut=jieba.cut(''.join(o.strip().split())) #斷詞
            li = []
            for u in Cut:
                if u.encode('utf-8') not in dot:  #清洗全形符號
                    li.append(u) #沒在dot裡的就寫進陣列
            n1 = (' '.join(li)).encode('utf-8') #將陣列用空白格開, 傳回字串
            w.write(n1+'\n') #寫入

#V5__結合
d = time.time()
print 'V4_Done!_Cost:',(d-c)

Ori = 0
Edi = 0
with open(Dir+'_5_Combine.txt',"w") as fid:
    for name in os.listdir(Dir+'_4'):
        In = Dir+'_4'+'//' + name
        #print 'OriLen',len([line for line in open(In)])
        Ori += len([line for line in open(In)])
        cnt = 0
        for i in open(In,'r'):
            if not i.strip() =='':
                cnt += 1
                fid.write(i.strip()+'\n')
        Edi += cnt
        #print 'EdiLen',cnt
print '\n---------------'
print 'Multiple_File_Combine_Ori-Len',"\t",Ori
print 'Multiple_File_Combine_CutEnptyLine-Len',"\t",Edi
print 'Final_Combine_File_Len',len([line for line in open(Dir+'_5_Combine.txt')])
print '---------------\n'

e = time.time()
print 'V5_Done!_Cost:',(e-d),'\n\n'

print 'All_Done!_TotalCost:',(e-a)
