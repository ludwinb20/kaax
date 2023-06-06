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
from kaax_app.models import Transacciones_Prueba, Empresa, Entrenamientos
from joblib import dump
import datetime
from .models import Verificaciones
from django.db.models import Q
from django.db.models.functions import ExtractWeek


def renovartoken():
    empresas = Empresa.objects.all()
    for empresa in empresas:
        token = secrets.token_urlsafe(32)
        empresa.token = token
        empresa.save()

        data = {'token': token}
        response = requests.post(empresa.endpoint_token, json=data)
        
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

    categorical_features = ['ip_address', 'email_address', 'billing_state', 'user_agent', 'billing_postal', 'phone_number', 'EVENT_TIMESTAMP', 'billing_address']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)])

    clf = DecisionTreeClassifier()

    pipe = Pipeline(steps=[('preprocessor', preprocessor),('classifier', clf)])

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print('Accuracy: %.2f' % accuracy)
    entrenamiento = Entrenamientos(precision=accuracy)
    entrenamiento.save()

    # guardar el modelo entrenado usando joblib
    feature_names = list(X.columns)
    dump(pipe, 'kaax/pesos/decision_tree.joblib')
    
    with open('kaax/pesos/feature_names.txt', 'w') as f:
        f.write('\n'.join(feature_names))
        
        
        
from django.db.models import Count
from django.db.models.functions import ExtractHour, ExtractWeekDay, ExtractMonth

def reporte(empresa_id, fecha_inicio, fecha_fin):
    # Obtener todos los registros de la empresa en el rango de fechas
    registros = Verificaciones.objects.filter(empresa_id=empresa_id, created_at__range=[fecha_inicio, fecha_fin])
    
    # 1. Conteo total de registros
    total_registros = registros.count()
    if total_registros == 0:
        resultados =  {
            'total_registros': 0,
            'total_fraud': 0,
            'porcentaje_fraud': 0,
            'total_legit': 0,
            'porcentaje_legit': 0,
            'fraud_por_hora': 0,
            'legit_por_hora': 0,
            'fraud_por_dia_semana': 0,
            'legit_por_dia_semana': 0,
            'fraud_por_semana': 0,
            'legit_por_semana': 0,
            'fraud_por_mes': 0,
            'legit_por_mes': 0,
        }
    else:
                # 2. Total de registros "fraud" y "legit" (cantidad y porcentaje del total)
        total_fraud = registros.filter(resultado='fraud').count()
        porcentaje_fraud = (total_fraud / total_registros) * 100
        total_legit = registros.filter(resultado='legit').count()
        porcentaje_legit = (total_legit / total_registros) * 100
        
        # 3. Total "fraud" por hora del día
        fraud_por_hora = registros.filter(resultado='fraud').annotate(hora=ExtractHour('created_at')).values('hora').annotate(count=Count('id')).order_by('hora')
        
        # 4. Total "legit" por hora del día
        legit_por_hora = registros.filter(resultado='legit').annotate(hora=ExtractHour('created_at')).values('hora').annotate(count=Count('id')).order_by('hora')
        
        # 5. Total "fraud" por día de la semana
        fraud_por_dia_semana = registros.filter(resultado='fraud').annotate(dia_semana=ExtractWeekDay('created_at')).values('dia_semana').annotate(count=Count('id')).order_by('dia_semana')
        
        # 6. Total "legit" por día de la semana
        legit_por_dia_semana = registros.filter(resultado='legit').annotate(dia_semana=ExtractWeekDay('created_at')).values('dia_semana').annotate(count=Count('id')).order_by('dia_semana')
        
        # 7. Total "fraud" por semana
        fraud_por_semana = registros.filter(resultado='fraud').annotate(semana=ExtractWeek('created_at')).values('semana').annotate(count=Count('id')).order_by('semana')
        
        # 8. Total "legit" por semana
        legit_por_semana = registros.filter(resultado='legit').annotate(semana=ExtractWeek('created_at')).values('semana').annotate(count=Count('id')).order_by('semana')
        
        # 9. Total "fraud" por mes
        fraud_por_mes = registros.filter(resultado='fraud').annotate(mes=ExtractMonth('created_at')).values('mes').annotate(count=Count('id')).order_by('mes')
        
        # 10. Total "legit" por mes
        legit_por_mes = registros.filter(resultado='legit').annotate(mes=ExtractMonth('created_at')).values('mes').annotate(count=Count('id')).order_by('mes')
        
        # Devolver los resultados en un diccionario
        resultados = {
            'total_registros': total_registros,
            'total_fraud': total_fraud,
            'porcentaje_fraud': porcentaje_fraud,
            'total_legit': total_legit,
            'porcentaje_legit': porcentaje_legit,
            'fraud_por_hora': fraud_por_hora,
            'legit_por_hora': legit_por_hora,
            'fraud_por_dia_semana': fraud_por_dia_semana,
            'legit_por_dia_semana': legit_por_dia_semana,
            'fraud_por_semana': fraud_por_semana,
            'legit_por_semana': legit_por_semana,
            'fraud_por_mes': fraud_por_mes,
            'legit_por_mes': legit_por_mes,
        }

    

    return resultados


