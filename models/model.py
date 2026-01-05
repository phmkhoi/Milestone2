from sklearn.linear_model import SGDClassifier
from sklearn.utils import shuffle
import numpy as np
from sklearn.metrics import log_loss
import copy
import json
import pickle
import os

class Model:
    def __init__(self):
        self.model = SGDClassifier(
            loss='log_loss', 
            learning_rate='optimal', 
            eta0=0.01,               
            early_stopping=False,    
            warm_start=True,     
        )
        self.dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def load(self, file_path):
        with open(file_path, "rb") as f:
            self.model = pickle.load(f)

    def train(self, vector, ground_truth, num_epoch=1000):
        best_loss = float('inf') 
        best_model = None
        self.classes = np.unique(ground_truth)
        for _ in range(num_epoch):
            X_train, y_train = shuffle(vector, ground_truth)
            self.model.partial_fit(X_train, y_train, self.classes)
            proba = self.model.predict_proba(vector)
            current_loss = log_loss(ground_truth, proba)
            if current_loss < best_loss:
                best_loss = current_loss
                best_model = copy.deepcopy(self.model)

        self.model = best_model
    
    def save_model(self, file_name):
        with open(file_name, mode='wb') as f:
            pickle.dump(self.model, f)

    def save_pred(self, file_name, ground_truth, prediction, type='test'):
        with open(file_name, mode='w', encoding='utf-8') as f:
            json.dump({
                "partition": type,
                "groundtruth":  ground_truth,
                "prediction": prediction
            }, f, indent=4)

    def predict_top_k(self, data, k, cite_to_arkiv, type='test'):
        for paper_id, papers in data.items():
            ground_truth = {}
            prediction = {}
            for entry_name, records in papers.items():
                if entry_name not in cite_to_arkiv:
                    continue
                vectors = []
                arkiv_ids = []
                for record in records:
                    vector = record["vector"]
                    arkiv_id = record['arkiv_id']
                    vectors.append(vector)
                    arkiv_ids.append(arkiv_id)

                proba = self.model.predict_proba(vectors)[:, -1]
                top_k_idx = np.argsort(proba)[-k:][::-1]
                # top_k_vals = proba[top_k_idx]
            
                ground_truth[entry_name] = cite_to_arkiv[entry_name]
                prediction[entry_name] = [arkiv_ids[i] for i in top_k_idx]
            file_name = os.path.join(self.dirname, paper_id, "pred.json")
            self.save_pred(file_name, ground_truth, prediction, type)

# print(ground_truth_valid)
# print(json.dumps(cite_arkiv_test, indent=4))
# print(log_loss(ground_truth_valid, proba))

#Can phai co cac bien
#Khi train va valid chi can 2 cai nay la du:
#vector_train: list[vector]: dung de train, valid
#ground_truth: list[]: [0, 1, 0, 1]

#Khi inferences:
#vector_train: "2306-14522": {
#     "Ziegel2016": [
#         {
#             "arkiv_id": "2007-082829",
#             "vector": [0,9, 1, 1]
#         },
            # {
            #     "arkiv"
            # }
#     ]
# }

#Tra ve gom 
#Ghi vao file giong pred.json
#Neu no la test thi tra ve top-k co format la:
# "2306-14522": {
#     "Ziegel2016": [
#         {
#             "arkiv_id": "2007-082829",
#             "prob": 0.9
#         }
#     ]
# }