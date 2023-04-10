from django.shortcuts import render
import csv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
import os
from .models import Transacciones_Prueba
import json

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

