#木のファイル入出力
#親（子の列）というラベルの文字列で出力


import copy
import sys
import time


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
#木のファイル出力・読み込み
##############################
#木のファイル出力

#木のルート => text
#text:親（子のリスト）というラベルの文字列
#ラベルが1文字でないとき、どうする？
#->''のようなラベルのまとまりを示す記号を使う
#->()でうまくやることは無理か？
def write_node(node):
	if node == None:	#このエラー処理は不要では？	
		return ''
	text = node.label
	#子を出力
	if node.children != []:
		text = text + '('
		for n in node.children:
			text = text + write_node(n)
		text = text + ')'
	return text


#木 => ファイル出力
def write_tree(tree, file):
	#木 => 文字列
	text = write_node(tree.root)
	with open(file, mode='w') as f:
		f.write(text)


#ファイル読み込み
#文字列 => 木
def read_tree(file):
	#ファイル読み込み
	with open(file) as f:
		str = f.read()

	#ルート作成
	tree = Tree()
	tree.add_root(str[0])
	if str[1] != '(':
		print('error: read_tree')
		sys.exit(1)
	#子を追加するノード
	n_t = tree.root

	#ルート以外のノード作成
	for i,c in enumerate(str[2:-1]):
		#print(i+3)
		if c == '(':
			n_t = n_t.children[-1]
			continue
		if c == ')':
			n_t = n_t.parent
			continue
		tree.add_children(n_t, [c])

	if str[-1] != ')' or n_t != tree.root:
		print('error: read_tree')
		sys.exit(1)

	return tree


'''
#動作確認（write_tree）
tree = Tree()
tree.add_root('R')
tree.add_children(tree.root, ['A','A'])
tree.add_children(tree.root.children[0], ['A','B','A','B'])
tree.add_children(tree.root.children[1], ['A','A','B'])

tree.print_tree()
write_tree(tree, 'tree_try.txt')

#動作確認（read_tree）
tree2 = read_tree('tree_try.txt')
tree2.print_tree()
'''
