from django.shortcuts import render
import csv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
import os
from .serializers import VerificacionesSerializer
from .models import Transacciones_Prueba, Empresa, Verificaciones
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
from joblib import dump, load
import datetime


@csrf_exempt
def entrenamiento_csv(request):
    filepath = ''
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            # Procesar el archivo CSV
            reader = csv.reader(archivo.read().decode('utf-8').splitlines())
            # Realizar cualquier operación con los datos del archivo
            archivo_original = archivo.name
            extension = archivo_original.split('.')[-1]  # Obtiene la extensión del archivo'
            if extension != 'csv':
                data = {'resultado': 'Petición Incorrecta: El formato del archivo no es .csv'}
                return JsonResponse(data, status=404)
            nombre_archivo = str(uuid.uuid4()) + '.' + extension

            filepath = os.path.join('kaax/datos', nombre_archivo)
            with open(filepath, 'wb+') as destination:
                    for chunk in archivo.chunks():
                        destination.write(chunk)
        else:
            data = {'resultado': 'Petición Incorrecta: No se adjunto archivo'}
            return JsonResponse(data, status=402)

    else:
        data = {'resultado': 'Petición Incorrecta: Se esperaba metodo POST'}
        return JsonResponse(data, status=401)

    with open(filepath, 'r') as archivo_csv:
        csv_reader = csv.reader(archivo_csv)
        columnas = next(csv_reader)
        if 'ip_address' in columnas and 'email_address' in columnas and 'billing_state' in columnas and 'user_agent' in columnas and 'billing_postal' in columnas and 'phone_number' in columnas and 'EVENT_TIMESTAMP' in columnas and 'billing_address' in columnas and 'EVENT_LABEL' in columnas:
            for row in csv_reader:
                transaccion = Transacciones_Prueba(
                    ip_address=row[0],
                    email_address=row[1],
                    billing_state=row[2],
                    user_agent=row[3],
                    billing_postal=row[4],
                    phone_number=row[5],
                    EVENT_TIMESTAMP=row[6],
                    billing_address=row[7],
                    EVENT_LABEL=row[8],
                    empresa_id=1,
                    archivo=nombre_archivo,
                )
                transaccion.save()
        else: 
            data = {'resultado': 'Peticion incorrecta: El archivo .csv no contiene las columnas necesarias'}
            return JsonResponse(data, status=403)

    data = {'resultado': 'exitoso'}
    return JsonResponse(data, status=200)



@csrf_exempt
def entrenamiento_json(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if data:
            if not all(key in data[0] for key in ('ip_address', 'email_address', 'billing_state', 'user_agent', 'billing_postal', 'phone_number', 'EVENT_TIMESTAMP', 'billing_address', 'EVENT_LABEL')):
                data = {'resultado': 'Petición Incorrecta: El objeto JSON no contiene las llaves necesarias'}
                return JsonResponse(data, status=404)

            for row in data:
                transaccion = Transacciones_Prueba(
                    ip_address=row['ip_address'],
                    email_address=row['email_address'],
                    billing_state=row['billing_state'],
                    user_agent=row['user_agent'],
                    billing_postal=row['billing_postal'],
                    phone_number=row['phone_number'],
                    EVENT_TIMESTAMP=row['EVENT_TIMESTAMP'],
                    billing_address=row['billing_address'],
                    EVENT_LABEL=row['EVENT_LABEL'],
                    empresa_id=1,
                    archivo='json'
                )
                transaccion.save()
        else:
            data = {'resultado': 'Petición Incorrecta: No se adjunto objeto JSON'}
            return JsonResponse(data, status=402)

    else:
        data = {'resultado': 'Petición Incorrecta: Se esperaba metodo POST'}
        return JsonResponse(data, status=401)

    data = {'resultado': 'exitoso'}
    return JsonResponse(data, status=200)


@csrf_exempt
@api_view(['POST'])
def verificar_transaccion(request):
    # validar campos necesarios
    required_fields = ['ip_address', 'email_address', 'billing_state', 'user_agent', 'billing_postal', 'phone_number', 'EVENT_TIMESTAMP', 'billing_address', 'empresa_id', 'token']
    for field in required_fields:
        if field not in request.data:
            return JsonResponse({'error': f'El campo {field} es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # verificar token de la empresa
    # # empresa_id = request.data['empresa_id']
    # # token = request.data['token']
    # # try:
    # #     empresa = Empresa.objects.get(id=empresa_id, token=token)
    # # except Empresa.DoesNotExist:
    # #     return JsonResponse({'error': 'Token de empresa inválido.'}, status=status.HTTP_401_UNAUTHORIZED)

    # cargar modelo y preprocesador
    clf = load('kaax/pesos/decision_tree.joblib')
    preprocessor = clf.named_steps['preprocessor']

    # leer datos de entrada
    with open('kaax/pesos/feature_names.txt', 'r') as f:
        feature_names = f.read().splitlines()
    
    input_data = pd.DataFrame(request.data, index=[0]).loc[:, feature_names]
    input_data_processed = preprocessor.transform(input_data)

    result = clf.predict(input_data_processed)



    verificacion = Verificaciones(
        ip_address=request.data['ip_address'],
        email_address=request.data['email_address'],
        billing_state=request.data['billing_state'],
        user_agent=request.data['user_agent'],
        billing_postal=request.data['billing_postal'],
        phone_number=request.data['phone_number'],
        EVENT_TIMESTAMP=request.data['EVENT_TIMESTAMP'],
        billing_address=request.data['billing_address'],
        resultado=result,
        empresa_id=request.data['empresa_id']
    )
    verificacion.save()

    # retornar resultado
    response_data = {'resultado': result}
    return Response(response_data)
