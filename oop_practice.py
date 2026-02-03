class Model:
    def __init__(self,name):
        self.name=name
        
        
    def predict(self,text):
            return f"Model {self.name} recieved:{text}"
model=Model("Dummy-AI")
print(model.predict("Hello AI"))