class Node:
    def __init__(self, content):
        self.content = content
        self.children = []
        
    def add_child(self, child_node):
        self.children.append(child_node)
        
        
class HierarchyTree:
    def __init__(self):
        self.levels = {
            'root': 0,
            'part': 1,
            'chapter': 2,
            'section': 3,
            'subsection': 4,
            'subsubsection': 5
        }
        
        self.root = Node('Document')
        self.stack = [(0, self.root)]
        
    def add_node(self, content, tag=None):
        if tag is None:
            parent_node = self.stack[-1][1]
            current_node = Node(content)
            parent_node.add_child(current_node)
            return
            
        current_level = self.levels.get(tag)
        
        if current_level is not None:
            while len(self.stack) > 1 and self.stack[-1][0] >= current_level:
                self.stack.pop()
                
            parent_node = self.stack[-1][1]
            current_node = Node(content)
            parent_node.add_child(current_node)
            
            self.stack.append((current_level, current_node))
            
    def print(self, node=None, level=0):
        if node is None:
            node = self.root
            
        print(' ' * level + f'├─{node.content}')
        
        for child in node.children:
            self.print(child, level + 1)
            
            
    def to_string(self, node=None, level=0):
        if node is None:
            node = self.root
            
        result = (' ' * level + f'├─{node.content}' + '\n')
        
        for child in node.children:
            result += self.to_string(child, level + 1)
            
        return result