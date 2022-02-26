#tree_mining_+dfs_simple2.ipynbより、bfs部分を抜粋
#tree_try.txtから木を読み込み、tree_freq.txtへ頻出順序木を出力
#tree_freq.txtではなく、ex2_bfs_sigma/result_(インプットファイル名).txtに出力 => 排除
#標準入力:ラベル集合、最低出現頻度
#tree_freq.txtへの出力:頻出木のサイズ 根頻度 順序木
#根頻度を保存するようfreqtを変更した
#error:freqtをn_nodeからn_node+1へ変更

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


#######################
#FREQT
#######################
#d_rmlを利用
#kノード順序木集合=>k+1ノード順序木集合
def make_alltree_sub(list_tree, list_label):
    ret  = []
    for t in list_tree:
        #最右枝の各ノードに最右葉追加
        for p in range(t.d_rml+1):
            for l in list_label:
                new = t.dup_tree()
                new.add_node(p, l)
                ret.append(new)
    return ret

#ｋノード順序木の列挙
def make_alltree(k, list_label):
    #1ノード順序木集合
    list_tree = []
    for l in list_label:
        new = Tree()
        new.add_root(l)
        list_tree.append(new)
    #k-1回木の拡張
    for i in range(k-1):
        list_tree = make_alltree_sub(list_tree, list_label)
    return list_tree


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


#FREQT
#データ木、ラベル集合、最低出現頻度　=> 頻出順序木リスト
def freqt(t_data, l_label, sig):
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
    k = 1
    #l_rmo:木の出現リストのリスト
    l_rmo = []
    for t in l_tree:
        l_rmo.append(rmo_one(t_data.root, t.root.label))
    #頻度で木を抽出
    #頻出木のl_treeにおけるインデックス
    index_t_freq = []
    for i,t in enumerate(l_tree):
        frequency = get_freq(t_data.n_node, l_rmo[i], 0)
        if frequency >= sig:
            l_t_freq.append(t)
            l_frequency.append(frequency)
            index_t_freq.append(i)
            #print('k=', k, ' ', get_freq(n_data, l_rmo[i], 0))
    #l_labelを最低頻度以上のlabel集合で置き換えるべき
    
    
    #rmoが空になるまで木の拡張を繰り返す
    while len(l_rmo) != 0:
        if k > t_data.n_node+1:
            print('error: freqt')
            break
        k += 1
        l_rmo_new = []
        l_tree_new = make_alltree_sub([l_tree[i] for i in index_t_freq], l_label)
        index_t_freq_new = []
        i = 0
        #l_treeの内、頻出だった各木
        for index in index_t_freq:
            #t = l_tree[index]
            #(p,l)-expansionした際のrmo
            for p in range(l_tree[index].d_rml+1):
                for l in l_label:
                    l_rmo_new.append(update_rmo(l_rmo[index], p, l))
                    #頻度で木を抽出
                    frequency = get_freq(t_data.n_node, l_rmo_new[i], l_tree_new[i].d_rml)
                    if frequency >= sig:
                        l_t_freq.append(l_tree_new[i])
                        l_frequency.append(frequency)
                        index_t_freq_new.append(i)
                    i += 1
        l_rmo = l_rmo_new
        l_tree = l_tree_new
        index_t_freq = index_t_freq_new

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

#l_label = ['A', 'B']
#sig = 0.1

#print('ファイル（データ木）')
file = input()

tree = write_read_tree.read_tree(file)
print('データ木のノード数:', tree.n_node)
tree.print_tree()
start = time.time()
l_t_freq, l_frequency = freqt(tree, l_label, sig)
end = time.time()
#print('time:', end-start)
print(end-start)

'''
#頻出木集合のファイル出力
text = ''
for t,frequency in zip(l_t_freq, l_frequency):
        text = text + str(t.n_node) + ' ' + str(frequency) + ' ' + write_read_tree.write_node(t.root) + '\n'
file_out = 'ex2_bfs_' + str(sig) + '/result_' + file[:-4] + '.txt'
'''

#頻出木集合のファイル出力
text = ''
for t,frequency in zip(l_t_freq, l_frequency):
	text = text + str(t.n_node) + ' ' + str(frequency) + ' ' + write_read_tree.write_node(t.root) + '\n'
with open('tree_freq.txt', mode='w') as f:
	f.write(text)

