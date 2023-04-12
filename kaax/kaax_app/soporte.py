import secrets
import requests
from .models import Empresa
from django.http import JsonResponse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import joblib
from kaax_app.models import Transacciones_Prueba, Empresa

def renovartoken():
    empresas = Empresa.objects.all()
    for empresa in empresas:
        token = secrets.token_urlsafe(32)
        empresa.token = token
        empresa.save()

        data = {'token': token}
        response = requests.post('http://ejemplo.com/tokens', json=data)
        
            # Verificar que la petición se haya realizado con éxito
        if response.status_code == 200:
            print('Token Enviado')
        else:
            print('Fallo en envio de token')

def entrenar():
    transacciones = Transacciones_Prueba.objects.exclude(empresa__isnull=True).values('ip_address', 'email_address', 'billing_state', 'user_agent', 'billing_postal', 'phone_number', 'EVENT_TIMESTAMP', 'billing_address', 'EVENT_LABEL')

    data = pd.DataFrame.from_records(transacciones)

    X = data.drop('EVENT_LABEL', axis=1)
    y = data['EVENT_LABEL']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_features = ['ip_address', 'email_address', 'billing_postal', 'phone_number', 'billing_address']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)])

    clf = DecisionTreeClassifier()

    pipe = Pipeline(steps=[('preprocessor', preprocessor),('classifier', clf)])

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print('Accuracy: %.2f' % accuracy)
    entrenamiento = Entrenamientos(precision=precision)
    entrenamiento.save()

    # guardar el modelo entrenado usando joblib
    dump(pipe, 'decision_tree.joblib')

