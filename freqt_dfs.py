#tree_mining_+dfs_simple2.ipynbより、bfs部分を抜粋
#tree_try.txtから木を読み込み、tree_freq.txtへ頻出順序木を出力
#標準入力:ラベル集合、最低出現頻度
#tree_freq.txtへの出力:頻出木のサイズ 根頻度 順序木
#根頻度を保存するようfreqt_dfsとfreqt_dfs_subを変更した

import copy
import sys
import time


import write_read_tree

###########################
#ノード、木の定義
###########################
class Node:
    def __init__(self, label, parent=None):
        #name:　木を全て作成した後、Treeのメソッドを呼び出すことでpreorderで順序付け
        self.name = 0    #なくても良いはず（深さ優先で1〜順序付け）（更新が煩雑）
        self.label = label
        self.parent = parent
        self.children = []    #上手い初期化があると良い(**********)
        self.sibling = None
        
class Tree:
    def __init__(self):
        self.root = None
        self.rml = None
        self.d_rml = None    #最右葉の深さ（ルート：０）
        self.n_node = 0       #ノードの数
    
    #ルートの追加
    def add_root(self, label):
        self.root = Node(label)
        self.rml = self.root
        self.d_rml = 0
        self.n_node = 1
    
    #指定ノードについて、子のラベルのリストによりノードを追加
    def add_children(self, pare, label_children):
        start = len(pare.children)
        #***************************************************************
        if start > 0:
            brother = pare.children[start-1]
        for i, label in enumerate(label_children):
            new = Node(label_children[i], parent  = pare)
            #n_nodeの更新
            self.n_node += 1
            pare.children.append(new)
            #*************************************************************
            if i == 0:
                if start > 0:
                    brother.sibling = new
                brother = new
            if i != 0:
                brother.sibling = new
                brother = new
        #rml, d_rmlの更新
        rml = self.root
        ind = 0
        while len(rml.children) > 0:
            rml = rml.children[-1]
            ind += 1
        self.rml = rml
        self.d_rml = ind
        

    #(p,l)-expansion
    #rmlからp個親側に遡ったノードの最右にラベルｌのノードを追加
    def add_node(self, p, l):
        #p > rmlの深さ　のエラー処理
        if p > self.d_rml:
            print(self.d_rml)
            print('error : add_node')
            sys.exit(1)
            
        #p = int(p)    必要？
        new = Node(l)
        #self.root == Noneの場合分け必要か？
        if p == 0:
            self.rml.children.append(new)
            new.parent = self.rml
            #self.rml = new    必要？
        else:
            v = self.rml
            for i in range(p-1):
                v = v.parent
            v.sibling = new
            new.parent = v.parent
            v.parent.children.append(new)
        #rml, d_rml, n_nodeの更新
        self.rml = new
        self.d_rml = self.d_rml-p+1
        self.n_node += 1
        
        
    #rmlの削除
    def del_rml(self):
            #1ノードの木の場合
            if self.root == self.rml:
                self.__init__()
                return
            #２ノード以上
            self.rml.parent.children.pop(-1)
            #兄存在
            if self.rml.parent.children != []:
                self.rml.parent.children[-1].sibling = None
            
            #rml, d_rml, n_nodeの更新
            rml = self.root
            ind = 0
            while len(rml.children) > 0:
                rml = rml.children[-1]
                ind += 1
            self.rml = rml
            self.d_rml = ind
            self.n_node -= 1

    #Node.nameをpreorderで順序付け
    def naming_sub(self, node, list_i):
        node.name = list_i[0]
        list_i[0] += 1
        if len(node.children) != 0:
            for n in node.children:
                self.naming_sub(n, list_i)
    
    def naming(self):
        list_i = [1]
        self.naming_sub(self.root, list_i)
                
    #木の出力
    def print_tree_pre(self, n, level):
        if n == None:
            print('Null')
            return
        print(n.label)
        if len(n.children) != 0:
            level += 1
            for i in n.children:
                for j in range(level):
                    print('ー', end='')
                self.print_tree_pre(i, level)
    def print_tree(self):
        self.print_tree_pre(self.root, 0)
    
    #木の出力（ノード番号あり）
    def printi_tree_pre(self, n, level):
        if n == None:
            print('Null')
            return
        print(n.label,'(', n.name, ')')
        if len(n.children) != 0:
            level += 1
            for i in n.children:
                for j in range(level):
                    print('ー', end='')
                self.printi_tree_pre(i, level)
    def printi_tree(self):
        self.printi_tree_pre(self.root, 0)
        
    #木の複製
    def dup_tree(self):
        new = copy.deepcopy(self)
        return new


##############################
#FREQT
##############################
#出現リストの更新
#データ木における元の木の出現リスト、p、ｌ => 拡張後の木の出現リスト
def update_rmo(rmo, p, l):
    new_rmo = []
    #重複した探索を避けるため、(p,l)-expansionで追加するノードの親を格納
    check = None
    
    for n in rmo:
        #print('update_rmo', n.name)
        #探索開始ノードがあるかどうかのフラグ
        f = 0
        if p == 0:
            #******************************************************************
            #len(n.children) == 0のとき、n=Noneになれば良い
            if len(n.children) == 0:
                continue
            n = n.children[0]
        else:
            #ｎをｐ-1親側に遡る
            for i in range(p-1):
                n = n.parent
                if n == None:
                    f = 1
                    break
            if f == 1:
                continue
            #元のｎのp個上のノードがcheckと同一か確認
            if n.parent == None:
                continue
            if n.parent == check:
                continue
            check = n.parent
            #nの弟を探索開始位置とする
            #if n.sibling != None:
            n = n.sibling
            
        
        #if n != None:
        #    print('start:', n.name)
        #nから順にラベルを確認
        while n != None:
            
            if n.label == l:
                new_rmo.append(n)
                #print(n.name)
            n = n.sibling
    return new_rmo


#頻度計算
#データ木のノード数、rmo、rmｌの深さ　=> 頻度
#深さ：rootで０
def get_freq(n_data, rmo, d_rml):
    l_rootocc = set()
    for n in rmo:
        for i in range(d_rml):
            n = n.parent
        l_rootocc.add(n)
    return len(l_rootocc)/n_data


#１ノード順序木の出現
def rmo_one(node, label):
    rmo = []
    if node.label == label:
        rmo.append(node)
    if len(node.children) == 0:
        return rmo
    else:
        for i in node.children:
            rmo = rmo + rmo_one(i, label)
        return rmo


#FREQT（DFS版）（標準出力でなく、頻出順序木リストを持つ）
#変更点：順序木のリスト不要、rmoもリストでなくて良い、再帰的に計算

#再帰的に頻出木発見
#t_patternを1ノード拡張して出来る木の内、頻出のものを返す
def freqt_dfs_sub(t_data, t_pattern, rmo, l_label, sig, l_t_freq, l_frequency):
    for p in range(t_pattern.d_rml+1):
        for l in l_label:
            #木の拡張
            t_pattern.add_node(p, l)
            #print('t_pattern')
            #t_pattern.print_tree()
            rmo_new = update_rmo(rmo, p, l)
            #頻出か
            frequency = get_freq(t_data.n_node, rmo_new, t_pattern.d_rml)
            if frequency >= sig:
                t = t_pattern.dup_tree()
                l_t_freq.append(t)
                l_frequency.append(frequency)
                freqt_dfs_sub(t_data, t_pattern, rmo_new, l_label, sig, l_t_freq, l_frequency)
            t_pattern.del_rml()

#データ木、ラベル集合、最低出現頻度　=> 頻出順序木リスト
def freqt_dfs(t_data, l_label, sig):
    #頻出順序木集合
    l_t_freq = []
    #頻出順序木集合の根頻度
    l_frequency = []

    #1ノードの順序木リスト
    l_tree = []
    for l in l_label:
        new = Tree()
        new.add_root(l)
        l_tree.append(new)
    #1ノード順序木の出現
    k = 1    #なくても良い（エラー出力に使用）
    #l_rmo:木の出現リストのリスト
    l_rmo = []
    for t in l_tree:
        l_rmo.append(rmo_one(t_data.root, t.root.label))
    #頻度で木を抽出
    ii = 0
    for i,t in enumerate(l_tree):
        #print('len', len(l_rmo))
        #print(i)
        frequency = get_freq(t_data.n_node, l_rmo[i-ii], 0)
        if frequency >= sig:
            l_t_freq.append(t)
            l_frequency.append(frequency)
        else:
            #l_rmoから頻出でない木の情報削除
            l_rmo.pop(i)
            ii += 1
    #l_treeから頻出でない木の情報削除
    l_tree = copy.deepcopy(l_t_freq)
    l_frequency_one = copy.deepcopy(l_frequency)
            
    #l_labelを最低頻度以上のlabel集合で置き換えるべき
    
    l_t_freq = []
    l_frequency = []
    #各1ノードの木について繰り返し
    for i,t in enumerate(l_tree):
        l_t_freq.append(t)
        l_frequency.append(l_frequency_one[i])
        freqt_dfs_sub(t_data, t, l_rmo[i], l_label, sig, l_t_freq, l_frequency)
    return l_t_freq, l_frequency

#######################
#実行
#######################
#標準入力よりパラメータ取得
print('ラベル')
l_label = input()
l_label = l_label.split()
print('最低出現頻度')
sig = float(input())
print('l_label = ', l_label)
print('sig = ', sig)

print('ファイル（データ木）')
file = input()
tree = write_read_tree.read_tree(file)
print('データ木のノード数:',tree.n_node)
#tree.print_tree()
start = time.time()
l_t_freq, l_frequency = freqt_dfs(tree, l_label, sig)
end = time.time()
print('time:', end-start)

#頻出木集合のファイル出力
text = ''
for t,frequency in zip(l_t_freq, l_frequency):
	text = text + str(t.n_node) + ' ' + str(frequency) + ' ' + write_read_tree.write_node(t.root) + '\n'
with open('tree_freq.txt', mode='w') as f:
	f.write(text)

