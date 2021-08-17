import re
import treetaggerwrapper as ttpw
import os
import csv
import time
class treenode():
    def __init__(self,date,dadnode):
        self.date=date#储存单词
        self.dadnode=dadnode#表示父节点位置
        self.count=1#计数
        self.next=-1#用于频次表中串联列表
        self.childnode={}#保存子节点和其在Tree中的位置下标
        self.label=False#用以保证频次表中一个节点只被使用一次

def create_dir_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)

def read_line(file):
    lines=[]
    with open(file,"r",encoding="utf-8") as f:
        lines=[ x[:-1].strip() if x.endswith("\n") else x.strip()   for x in f.readlines() ]
    return lines

def handle_texts(tagger,texts, default_word, stoptags, stopwords, stop_start, stop_end,ty,label=True):
    #handle_texts(tagger,[word_file], default_word, stop_pos, stop_words, stop_start, stop_end,label=True)
    print(default_word)
    result=[]
    knu=0
    for tt in texts:
        knu+=1
        print(knu)
        with open(tt,"r",encoding="utf-8") as f:
            words=[]
            while True:
                text_line=f.readline()
                if text_line:
                    if text_line.endswith("\n"):
                        text_line=text_line[:-1].strip()
                    else:
                        text_line=text_line.strip()
                    words_line=re.sub(r" '","'",text_line)
                    words_line=re.sub(r"' ","'",words_line)
                    tags = tagger.tag_text(words_line)
                    tags2 = ttpw.make_tags(tags, allow_extra=True)      
                    line=[]
                    for i in tags2:
                        #print(i)
                        try:
                            ggu=i.lemma
                        except:
                            continue
                        if i.lemma in ["<unknown>",'@ord@','@card@']:#解决还原异常
                            word=(i.word, i.word)
                        else:
                            word=(i.word,i.lemma)
                        if word in default_word:#一些不当还原的重新返回去（比如英文单词在法语中还原不当）
                            word=(word[0],word[0])
                        if i.pos not in stoptags and word[1] not in stopwords:#停用词性和停用词表拆分词组
                            line.append(word[1])
                        else:
                            if line:
                                for item in range(len(line)):
                                    if line[item] not in stop_start:#以“de","du"开头的，将其删掉
                                        break
                                line=line[item:]

                                while line[-1] in stop_end:
                                    line=line[:-1]

                                if line:
                                    words.append(line)
                                line=[]
                            else:
                                continue
                else:
                    break
            if label==True:
                if ty=="file":
                    kl=os.path.split(tt)
                    with open(os.path.join(kl[0],"_FP"+kl[1]),"w", encoding="utf-8") as g:
                        for w in words:
                            g.write(" ".join(w)+"\n")
                elif ty=="dir":
                    kl=os.path.split(tt)
                    create_dir_not_exist(kl[0]+"FP_")
                    with open(os.path.join(kl[0]+"FP_","FP_"+kl[1]),"w", encoding="utf-8") as g:
                        for w in words:
                            g.write(" ".join(w)+"\n")
            result+=words
    return result
                


language=input("请输入需处理的语言(英语 en;法语 fr;)：")
while not language:
    print("输入不合法！")
    language=input("请输入需处理的语言(英语 en;法语 fr;)：")

stop_pos_file=input("请输入停用词性表文件名(txt文件，一行一个)，否则点击回车使用默认：")
stop_words_file=input("请输入停用词文件名(txt文件，一行一个)，否则点击回车使用默认：")
stop_start_file=input("请输入需要删除的词组前缀文件名(txt文件，一行一个)，否则点击回车使用默认：")
stop_end_file=input("请输入需要删除的词组后缀文件名(txt文件，一行一个)，否则点击回车使用默认：")
default_word_file=input("请输入默认不还原的词组文件(txt文件，一行一个)，否则点击回车使用默认：")
hande_Substring=input("请输入提词时是否删除子串，删除输入1，不删除输入2：")
word_file=input("请输入需要处理的文件路径：")

if not stop_pos_file:
    path=os.path.join(os.path.dirname(__file__),language)
    stop_pos=read_line(os.path.join(path,language+"_default_stop_pos.txt"))
else:
    stop_pos=read_line(stop_pos_file)
stop_pos=set(stop_pos)

if not stop_words_file:
    path=os.path.join(os.path.dirname(__file__),language)
    stop_words=read_line(os.path.join(path,language+"_default_stop_words.txt"))
else:
    stop_words=read_line(stop_words_file)
stop_words=set(stop_words)

if not stop_start_file:
    path=os.path.join(os.path.dirname(__file__),language)
    stop_start=read_line(os.path.join(path,language+"_default_stop_start.txt"))
else:
    stop_start=read_line(stop_start_file)
stop_start=set(stop_start)

if not stop_end_file:
    path=os.path.join(os.path.dirname(__file__),language)
    stop_end=read_line(os.path.join(path,language+"_default_stop_end.txt"))
else:
    stop_end=read_line(stop_end_file)
stop_end=set(stop_end)

if not default_word_file:
    path=os.path.join(os.path.dirname(__file__),language)
    default_word=read_line(os.path.join(path,language+"_default_word.txt"))
else:
    default_word=read_line(default_word_file)
line_default_word=set([])
for i in default_word:
    line_default_word.add((i.split(':')[0],i.split(':')[1]))

tagger = ttpw.TreeTagger(TAGLANG=language)
if os.path.isfile(word_file):
    if word_file.endswith('.txt'):
        words=handle_texts(tagger,[word_file], line_default_word, stop_pos, stop_words, stop_start, stop_end,"file",label=True)
    else:
        raise ValueError("please use .txt")
elif os.path.isdir(word_file):
    file_list=[os.path.join(word_file, x)  for x in os.listdir(word_file) if x.endswith(".txt")]
    words=handle_texts(tagger,file_list, line_default_word, stop_pos, stop_words, stop_start, stop_end,"dir",label=True)
else:
    raise ValueError("please use .txt file or dir")
start=time.time()
print(len(words))
#建树，并存储所有末端叶子结点
Tree=[]#储存树
leaf=[]#储存末端叶子结点，每一个新建的节点先放进来，当第一次更新它的子节点字典时，将它踢出来
root=treenode('根节点',-1)#根节点，-1为哨兵，方便从下往上输出
Tree.append(root)
leaf.append(0)
knum=0
for i in words:#遍历词组
    knum+=1
    print(knum)
    e=0#e为指针，每一个新词组都返回根节点重新查询
    for j in range(len(i)):#遍历一个句子内的单词      
        #while j<len(i):#遍历从当前单词开始到句子结束的所有单词
        if i[j] not in Tree[e].childnode.keys():
            #如果当前单词不在当前节点的子节点字典内，就更新子节点字典，这个子节点所在的下标是当前Tree的len(Tree)。新建一个节点放入Tree中，此时Tree长度增加一，所以指针指向新建的节点在Tree中的位置下标len(Tree)-1
            if e in leaf:#记录叶子节点
                leaf.remove(e)
            Tree[e].childnode[i[j]]=len(Tree)
            node=treenode(i[j],e)
            Tree.append(node)
            e=len(Tree)-1
            leaf.append(e)
            j+=1
        else:
            #如果当前单词在当前节点的子节点字典内，就将指针移到当前单词所在的节点
            e=Tree[e].childnode[i[j]]
            Tree[e].count+=1
            j+=1

#建立频次表
frequency_table={}
for i in leaf:
    k=i
    num=Tree[k].count-1
    while k!=0:
        if Tree[k].count>num:
            
            try:
                frequency_table[Tree[k].count]
            except KeyError:
                frequency_table[Tree[k].count]=[k, k]
                Tree[k].label=True
            else:
                if not Tree[k].label:
                    Tree[k].label=True
                    Tree[frequency_table[Tree[k].count][1]].next=k
                    frequency_table[Tree[k].count][1]=k
            num=Tree[k].count

        k=Tree[k].dadnode

print(time.time()-start)

key_line=sorted(frequency_table.keys())
threshold=2
result=[]
if hande_Substring=="1":
#删子串
    for i in key_line:
        if i>=threshold:
            node_item=frequency_table[i][0]
            while node_item!=-1:
                if Tree[node_item].count<threshold:
                    node_item=Tree[node_item].next
                    continue
                line=[]
                line_node_item=node_item
                num=Tree[line_node_item].count
                while Tree[line_node_item].dadnode!=-1:
                    line.append(Tree[line_node_item].date)
                    Tree[line_node_item].count-=num
                    line_node_item=Tree[line_node_item].dadnode
                line.reverse()
                result.append([line,num])
                node_item=Tree[node_item].next
else:
#不删子串
    for i in key_line:
        if i>=threshold:
            node_item=frequency_table[i][0]
            while node_item!=-1:
                if Tree[node_item].count<threshold:
                    node_item=Tree[node_item].next
                    continue
                line=[]
                line_node_item=node_item
                num=Tree[line_node_item].count
                while Tree[line_node_item].dadnode!=-1:
                    line.append(Tree[line_node_item].date)
                    line_node_item=Tree[line_node_item].dadnode
                line.reverse()
                result.append([line,num])
                node_item=Tree[node_item].next

rows=[[' '.join(x[0]), x[1]] for x in result]

headers=["phrase","freuqency"]
with open('result.csv','w', encoding="utf-8")as f:
    f_csv = csv.writer(f)
    f_csv.writerow(headers)
    f_csv.writerows(rows)



