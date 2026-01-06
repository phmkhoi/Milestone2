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

    def train(self, vector_train, ground_truth_train, vector_valid, ground_truth_valid, num_epoch=1000):
        best_loss = float('inf') 
        best_model = None
        self.classes = np.unique(ground_truth_train)
        for _ in range(num_epoch):
            X_train, y_train = shuffle(vector_train, ground_truth_train)
            self.model.partial_fit(X_train, y_train, self.classes)
            proba = self.model.predict_proba(vector_valid)
            current_loss = log_loss(ground_truth_valid, proba)
            if current_loss < best_loss:
                best_loss = current_loss
                best_model = copy.deepcopy(self.model)

        self.model = best_model
    
    def save_model(self, file_name):
        with open(file_name, mode='wb') as f:
            pickle.dump(self.model, f)

    def save_pred(self, file_name, ground_truth, prediction, type='test'):
        object = {
            "partition": type,
            "groundtruth":  ground_truth,
            "prediction": prediction
        }
        with open(file_name, mode='w', encoding='utf-8') as f:
            json.dump(object, f, indent=4)

    def predict_top_k(self, data, k, cite_to_arkiv, type='test', return_object=False):
        save_pred_json = []
        
        for paper_id, papers in data.items():
            ground_truth = {}
            prediction = {}
            for entry_name, records in papers.items():
                if entry_name not in cite_to_arkiv:
                    continue
                vectors = []
                arxiv_ids = []
                for record in records:
                    vector = record["vector"]
                    arxiv_id = record['arxiv_id']
                    vectors.append(vector)
                    arxiv_ids.append(arxiv_id)

                proba = self.model.predict_proba(vectors)[:, -1]
                top_k_idx = np.argsort(proba)[-k:][::-1]
                # top_k_vals = proba[top_k_idx]
            
                ground_truth[entry_name] = cite_to_arkiv[entry_name]
                prediction[entry_name] = [arxiv_ids[i] for i in top_k_idx]
            file_name = os.path.join(self.dirname, paper_id, "pred.json")
            self.save_pred(file_name, ground_truth, prediction, type)
            
            if return_object:
                file_test_name = os.path.join(self.dirname, 'eval',  f"pred_{paper_id.split('/')[-1]}.json")
                self.save_pred(file_test_name, ground_truth, prediction, type)