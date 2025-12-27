class HierarchyManager:
    def __init__(self):
        self.content_to_id = {}
        self.output = {}
        self.counter = 1
        
    def get_id(self, content):
        if content is None:
            content = ''
            
        if content in self.content_to_id:
            return self.content_to_id[content]
        
        id = f'id-string-{self.counter}'
        self.counter += 1
        
        self.content_to_id[content] = id
        self.output[id] = content
    
        return id