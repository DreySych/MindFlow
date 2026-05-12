from sentence_transformers import SentenceTransformer
import os

_model = None
LOCAL_MODEL_PATH = "my_local_model"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def get_model():
    global _model
    if _model is None:
        if os.path.exists(LOCAL_MODEL_PATH):
            _model = SentenceTransformer(LOCAL_MODEL_PATH, local_files_only=True)
        else:
            _model = SentenceTransformer(MODEL_NAME)
            _model.save_pretrained(LOCAL_MODEL_PATH)
    return _model
