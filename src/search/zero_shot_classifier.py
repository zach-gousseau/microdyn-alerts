from transformers import pipeline
from sentence_transformers import CrossEncoder

# class UpdateClassifier:
#     def __init__(self):
#         self.nlp_model = pipeline("zero-shot-classification")

#     def is_update(self, paragraph):
#         candidate_labels = [
#             "update",
#             "no update",
#         ]
#         result = self.nlp_model(paragraph, candidate_labels)
#         return result['labels'][0] == 'update'
    
class UpdateClassifier:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/nli-deberta-v3-small')

    def is_update(self, paragraph):
        candidate_labels = [
            "update",
            "no update",
        ]
        scores = self.model.predict([(paragraph, label) for label in candidate_labels])
        
        # choose the label with the highest score
        if candidate_labels[scores.argmax()] == "This paragraph contains a regulatory update.":
            return True
        
        return False
