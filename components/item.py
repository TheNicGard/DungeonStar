class Item:
    def __init__(self, count, max_age=None, use_function=None, targeting=False, targeting_message=None, **kwargs):
        self.count = count
        
        self.max_age = max_age
        self.age = None
        if self.max_age:
            self.age = 0
            
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs
