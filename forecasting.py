import joblib

def load_model():
    return joblib.load('model.joblib')

def load_xunique():
    return joblib.load('xunique.joblib')

def predict(data):
    model = load_model()
    yenc = joblib.load('yenc.joblib')
    value = model.predict(data)
    return yenc.inverse_transform(value)
