class HierarchyManager:
    def __init__(self):
        self.content_to_id = {}
        self.output = {}
        self.counter = {}
        
    def get_id(self, content, paper_id):
        if content is None:
            content = ''
        
        if content in self.content_to_id:
            return self.content_to_id[content]
        
        if paper_id not in self.counter.keys():
            self.counter[str(paper_id)] = 1
        
        id = f'{paper_id}-{self.counter[str(paper_id)]}'
        self.counter[str(paper_id)] += 1
        
        self.content_to_id[content] = id
        self.output[id] = content
    
        return id