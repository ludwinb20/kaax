from django.shortcuts import render
import csv
from django.http import JsonResponse, HttpResponse,FileResponse
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
from datetime import datetime,timedelta
from kaax_app.soporte import reporte
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Border, Side
import matplotlib.pyplot as plt
import pdfkit
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.graphics.shapes import Rect

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
    required_fields_transaccion = ['ip_address', 'email_address', 'billing_state', 'user_agent', 'billing_postal', 'phone_number', 'EVENT_TIMESTAMP', 'billing_address']
    required_fields_empresa = ['empresa_id', 'token']
    
    for field in required_fields_empresa:
        if field not in request.data:
            return JsonResponse({'error': f'El campo {field} es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
    for field in required_fields_transaccion:
        if field not in request.data['transaccion']:
            return JsonResponse({'error': f'El campo {field} es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
    # verificar token de la empresa
    # # empresa_id = request.data['empresa_id']
    # # token = request.data['token']
    # # try:
    # #     empresa = Empresa.objects.get(id=empresa_id, token=token)
    # # except Empresa.DoesNotExist:
    # #     return JsonResponse({'error': 'Token de empresa inválido.'}, status=status.HTTP_401_UNAUTHORIZED)
    transaccion = request.data['transaccion']
    # cargar modelo y preprocesador
    pipe = load('kaax/pesos/decision_tree.joblib')
    
    df = pd.DataFrame(transaccion, index=[0])

    result = pipe.predict(df)



    verificacion = Verificaciones(
        ip_address=transaccion['ip_address'],
        email_address=transaccion['email_address'],
        billing_state=transaccion['billing_state'],
        user_agent=transaccion['user_agent'],
        billing_postal=transaccion['billing_postal'],
        phone_number=transaccion['phone_number'],
        EVENT_TIMESTAMP=transaccion['EVENT_TIMESTAMP'],
        billing_address=transaccion['billing_address'],
        resultado=result,
        empresa_id=request.data['empresa_id']
    )
    verificacion.save()

    # retornar resultado
    response_data = {'resultado': result}
    return Response(response_data)


@csrf_exempt
@api_view(['POST'])
def verificar_multiple(request):
    required_fields_transaccion = ['ip_address', 'email_address', 'billing_state', 'user_agent', 'billing_postal', 'phone_number', 'EVENT_TIMESTAMP', 'billing_address']
    required_fields_empresa = ['empresa_id', 'token']
    
    for field in required_fields_empresa:
        if field not in request.data:
            return JsonResponse({'error': f'El campo {field} es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

    # verificar token de la empresa
    empresa_id = request.data['empresa_id']
    token = request.data['token']
    try:
        empresa = Empresa.objects.get(id=empresa_id, token=token)
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Token de empresa inválido.'}, status=status.HTTP_401_UNAUTHORIZED)
        
    transacciones = request.data['transacciones']
    print(transacciones)
    pipe = load('kaax/pesos/decision_tree.joblib')
    i = 1
    respuesta = []
    
    for transaccion in transacciones:
        for field in required_fields_transaccion:
            if field not in transaccion:
                return JsonResponse({'error': f'Falta el campo {field} en la transaccion #{i}'}, status=status.HTTP_400_BAD_REQUEST)
        df = pd.DataFrame(transaccion, index=[0])
            
        result = pipe.predict(df)

        verificacion = Verificaciones(
            ip_address=transaccion['ip_address'],
            email_address=transaccion['email_address'],
            billing_state=transaccion['billing_state'],
            user_agent=transaccion['user_agent'],
            billing_postal=transaccion['billing_postal'],
            phone_number=transaccion['phone_number'],
            EVENT_TIMESTAMP=transaccion['EVENT_TIMESTAMP'],
            billing_address=transaccion['billing_address'],
            resultado=result,
            empresa_id=request.data['empresa_id']
        )
        
        verificacion.save()
            
        arreglo = {"transaccion": i, "resultado": result[0]}
            
        respuesta.append(arreglo)
        i=i+1
        
    return Response(respuesta)

@csrf_exempt
@api_view(['GET'])
def reporte_excel(request):
    required_fields = ['fechaInicial', 'fechaFinal', 'token', 'id']
    
    for field in required_fields:
        if field not in request.data:
            return JsonResponse({'error': f'El campo {field} es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        
    
    # empresa_id = request.data['empresa_id']
    # token = request.data['token']
    # try:
    #     empresa = Empresa.objects.get(id='id', token=token)
    # except Empresa.DoesNotExist:
    #     return JsonResponse({'error': 'Token de empresa inválido.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    formato_esperado = '%Y-%m-%d'
    
    try:
        datetime.strptime(request.data['fechaInicial'], formato_esperado)
        datetime.strptime(request.data['fechaFinal'], formato_esperado)
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha no valido(El formato debe ser yyyy-mm-dd, ejemplo: 2023-05-11)'}, status=status.HTTP_401_UNAUTHORIZED)
    
    datos = reporte(1, request.data[ 'fechaInicial'], request.data['fechaFinal'])
    
        # Extraer los datos relevantes
    total_registros = datos["total_registros"]
    total_fraud = datos["total_fraud"]
    porcentaje_fraud = datos["porcentaje_fraud"]
    total_legit = datos["total_legit"]
    porcentaje_legit = datos["porcentaje_legit"]
    fraud_por_hora = datos["fraud_por_hora"]
    legit_por_hora = datos["legit_por_hora"]
    fraud_por_dia_semana = datos["fraud_por_dia_semana"]
    legit_por_dia_semana = datos["legit_por_dia_semana"]
    fraud_por_semana = datos["fraud_por_semana"]
    legit_por_semana = datos["legit_por_semana"]
    fraud_por_mes = datos["fraud_por_mes"]
    legit_por_mes = datos["legit_por_mes"]

    # Crear un DataFrame de pandas con los datos
    
    categorias = ["Total Registros", "Total Fraudulentas", "Porcentaje Fraudulentas", "Total Legitimas", "Porcentaje Legitimas", " "]
    valores = [total_registros, total_fraud, porcentaje_fraud, total_legit, porcentaje_legit, ' ']

    # Agregar los datos por hora del día
    for item in fraud_por_hora:
        categorias.append(f"Fraudes por Hora {item['hora']}")
        valores.append(item['count'])
            
    for item in legit_por_hora:
        categorias.append(f"Legitimas por Hora {item['hora']}")
        valores.append(item['count'])
    
    categorias.append(' ')
    valores.append(' ')

    # Agregar los datos por día de la semana
    for item in fraud_por_dia_semana:
        categorias.append(f"Fraudes por Día {item['dia_semana']}")
        valores.append(item['count'])
    for item in legit_por_dia_semana:
        categorias.append(f"Legitimas por Día {item['dia_semana']}")
        valores.append(item['count'])

    categorias.append(' ')
    valores.append(' ')
    # Agregar los datos por semana

    for item in fraud_por_semana:
        categorias.append(f"Fraudes por Semana {item['semana']}")
        valores.append(item['count'])
    for item in legit_por_semana:
        categorias.append(f"Legitimas por Semana {item['semana']}")
        valores.append(item['count'])

    categorias.append(' ')
    valores.append(' ')
    # Agregar los datos por mes
 
    for item in fraud_por_mes:
        categorias.append(f"Fraudes por Mes {item['mes']}")
        valores.append(item['count'])
    for item in legit_por_mes:
        categorias.append(f"Legitimas por Mes {item['mes']}")
        valores.append(item['count'])

    
    df = pd.DataFrame({ "Categoría": categorias, "Valores":  valores})
    
    # Crear un libro de trabajo de Excel
    wb = Workbook()
    # Seleccionar la hoja de cálculo activa (por defecto es la primera hoja)
    ws = wb.active

    # Definir los estilos de celda
    header_fill = PatternFill(start_color="1e4d70", end_color="1e4d70", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    value_fill = PatternFill(start_color="72e082", end_color="72e082", fill_type="solid")
    value_font = Font(color="FFFFFF")
    border = Border(left=Side(border_style="thin", color="000000"),
                right=Side(border_style="thin", color="000000"),
                top=Side(border_style="thin", color="000000"),
                bottom=Side(border_style="thin", color="000000"))

    # Aplicar formato a la primera fila (encabezados)
    for col_num, value in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_num, value=value)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border

    # Aplicar formato a las celdas de valores
    for row_num, row_data in enumerate(df.values, 2):
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.fill = value_fill
            # cell.font = value_font
            cell.border = border

    # Ajustar el ancho de las columnas automáticamente
    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

    # Guardar el libro de trabajo
    archivo_excel = os.path.join('reporteria', 'reporte.xlsx')
    df.to_excel(archivo_excel, index=False)

    # Leer el archivo Excel generado
    with open(archivo_excel, 'rb') as file:
        excel_content = file.read()

    # Configurar la respuesta HTTP con el archivo Excel adjunto
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte.xlsx"'
    response.write(excel_content)

    return response


@csrf_exempt
@api_view(['GET'])
def reporte_graficas(request):
    required_fields = ['fechaInicial', 'fechaFinal', 'token', 'id']
    
    for field in required_fields:
        if field not in request.data:
            return JsonResponse({'error': f'El campo {field} es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        
    
    # empresa_id = request.data['empresa_id']
    # token = request.data['token']
    # try:
    #     empresa = Empresa.objects.get(id='id', token=token)
    # except Empresa.DoesNotExist:
    #     return JsonResponse({'error': 'Token de empresa inválido.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    formato_esperado = '%Y-%m-%d'
    
    try:
        datetime.strptime(request.data['fechaInicial'], formato_esperado)
        datetime.strptime(request.data['fechaFinal'], formato_esperado)
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha no valido(El formato debe ser yyyy-mm-dd, ejemplo: 2023-05-11)'}, status=status.HTTP_401_UNAUTHORIZED)
    
    datos = reporte(1, request.data[ 'fechaInicial'], request.data['fechaFinal'])

    total_registros = datos["total_registros"]
    total_fraud = datos["total_fraud"]
    porcentaje_fraud = datos["porcentaje_fraud"]
    total_legit = datos["total_legit"]
    porcentaje_legit = datos["porcentaje_legit"]
    fraud_por_hora = datos["fraud_por_hora"]
    legit_por_hora = datos["legit_por_hora"]
    fraud_por_dia_semana = datos["fraud_por_dia_semana"]
    legit_por_dia_semana = datos["legit_por_dia_semana"]
    fraud_por_semana = datos["fraud_por_semana"]
    legit_por_semana = datos["legit_por_semana"]
    fraud_por_mes = datos["fraud_por_mes"]
    legit_por_mes = datos["legit_por_mes"]

    ancho_pagina = 600
    alto_pagina = 800
    ancho_grafico = ancho_pagina / 3
    alto_grafico = alto_pagina / 3

    c = canvas.Canvas('reporteria/graficos.pdf', pagesize=letter)

    # Inicializar el índice
    index = 0

    x = 0
    y = 0

    # Agregar el objeto Rect al Drawing
    drawing = Drawing(ancho_grafico, alto_grafico)
    borde = Rect(0, 0, ancho_grafico, alto_grafico)
    borde.strokeColor = colors.black
    borde.strokeWidth = 1
    drawing.add(borde)

    pie = Pie()
    pie.x = ancho_grafico / 2
    pie.y = alto_grafico / 2
    pie.width = ancho_grafico
    pie.height = alto_grafico
    pie.data = [total_fraud, total_legit]
    pie.labels = ['Total fraudes', 'Total Legitimas']
    pie.slices.strokeWidth = 0.5
    pie.slices.fontName = 'Helvetica-Bold'
    pie.slices.fontSize = 8
    pie.slices.labelRadius = 0.7
    pie.slices.strokeColor = colors.white

    drawing.add(pie)
    drawing.drawOn(c, x, y)

    x += ancho_grafico

    drawing2 = Drawing(ancho_grafico, alto_grafico)

    pie2 = Pie()
    pie2.x = ancho_grafico / 2
    pie2.y = alto_grafico / 2
    pie2.width = ancho_grafico
    pie2.height = alto_grafico
    pie2.data = [porcentaje_fraud, porcentaje_legit]
    pie2.labels = ['Porcentaje fraudes', 'Porcentaje Legitimas']
    pie2.slices.strokeWidth = 0.5
    pie2.slices.fontName = 'Helvetica-Bold'
    pie2.slices.fontSize = 8
    pie2.slices.labelRadius = 0.7
    pie2.slices.strokeColor = colors.white

    drawing2.add(pie2)
    drawing2.drawOn(c, x, y)

    x += ancho_grafico

    categorias = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    valoresf = []
    valoresl = []

    for hora in categorias:
        contador = 0
        for item in fraud_por_hora:
            if item['hora'] == hora:
                valoresf.append(item['count'])
                contador = 1
        if contador == 0:
            valoresf.append(0)

    for hora in categorias:
        contador = 0
        for item in legit_por_hora:
            if item['hora'] == hora:
                valoresl.append(item['count'])
                contador = 1
        if contador == 0:
            valoresl.append(0)

    drawing3 = Drawing(ancho_grafico, alto_grafico)
    data = [valoresl, valoresf]
    chart = VerticalBarChart()
    chart.x = ancho_grafico / 4
    chart.y = alto_grafico / 4
    chart.width = ancho_grafico / 2
    chart.height = alto_grafico / 2
    chart.data = data
    chart.categoryAxis.categoryNames = [str(h) for h in categorias]
    chart.bars[0].fillColor = colors.red
    chart.bars[1].fillColor = colors.green

    drawing3.add(chart)
    drawing3.drawOn(c, x, y)

    c.showPage()
    # c.save()

    
    categorias = [1, 2, 3, 4, 5, 6, 7]
    categoriasN = ['Domingo', 'Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado']
    valoresf = []
    valoresl = []

    for dia in categorias:
        contador = 0
        for item in fraud_por_dia_semana:
            if item['dia_semana'] == dia:
                valoresf.append(item['count'])
                contador = 1
        if contador == 0:
            valoresf.append(0)

    for dia in categorias:
        contador = 0
        for item in legit_por_dia_semana:
            if item['dia_semana'] == dia:
                valoresl.append(item['count'])
                contador = 1
        if contador == 0:
            valoresl.append(0)

    drawing6 = Drawing(ancho_grafico, alto_grafico)
    data = [valoresl, valoresf]
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.width = 300
    chart.height = 100
    chart.data = data
    chart.categoryAxis.categoryNames = [str(h) for h in categoriasN]
    chart.bars[0].fillColor = HexColor("#FF0000")  # Color para la categoría "Legit"
    chart.bars[1].fillColor = HexColor("#00FF00")  # Color para la categoría "Fraud"

    x = 0
    drawing6.add(chart)
    drawing6.drawOn(c, x ,y)
    
    numeros_semana = []
    nombres_semana = []
    valoresf = []
    valoresl = []

    # Agregar un día extra a la fecha de fin para asegurarse de incluir la última semana completa
    
    final = datetime.strptime(request.data['fechaFinal'], "%Y-%m-%d") + timedelta(days=1)

    # Iterar por cada día entre las fechas de inicio y fin
    fecha_actual = datetime.strptime(request.data['fechaInicial'], "%Y-%m-%d")
    while fecha_actual < final:
        numero_semana = fecha_actual.isocalendar()[1]  # Obtener el número de semana
        numeros_semana.append(numero_semana)
        fecha_actual += timedelta(days=1)  # Avanzar al siguiente día

    for semana in numeros_semana:
        contador = 0
        nombres_semana.append(f"Semana {semana}")
        for item in fraud_por_semana:
            if item['semana'] == semana:
                valoresf.append(item['count'])
                contador = 1
        if contador == 0:
            valoresf.append(0)
    
    for semana in numeros_semana:
        contador = 0
        for item in legit_por_semana:
            if item['semana'] == semana:
                valoresl.append(item['count'])
                contador = 1
        if contador == 0:
            valoresl.append(0)
    
    drawing4 = Drawing(ancho_grafico, alto_grafico)
    data = [valoresl, valoresf]
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.width = 300
    chart.height = 100
    chart.data = data
    chart.categoryAxis.categoryNames = [str(h) for h in nombres_semana]
    chart.bars[0].fillColor = HexColor("#FF0000")  # Color para la categoría "Legit"
    chart.bars[1].fillColor = HexColor("#00FF00")  # Color para la categoría "Fraud"
    
    x = ancho_grafico
    
    drawing4.add(chart)
    drawing4.drawOn(c, x, y)
    
    numeros_mes = []
    valoresf = []
    valoresl = []


    # Agregar un día extra a la fecha de fin para asegurarse de incluir la última semana completa
    final = datetime.strptime(request.data['fechaFinal'], "%Y-%m-%d") + timedelta(days=1)


    # Iterar por cada día entre las fechas de inicio y fin
    fecha_actual = datetime.strptime(request.data['fechaInicial'], "%Y-%m-%d").replace(day=1)

    while fecha_actual < final:
        numero_mes = fecha_actual.month  # Obtener el número de mes
        numeros_mes.append(numero_mes)
        fecha_actual = fecha_actual.replace(day=1)  # Avanzar al primer día del siguiente mes

        # Calcular el siguiente mes
        if fecha_actual.month == 12:
            fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
        else:
            fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)

    
    for mes in numeros_mes:
        contador = 0
        for item in fraud_por_mes:
            if item['mes'] == mes:
                valoresf.append(item['count'])
                contador = 1
        if contador == 0:
            valoresf.append(0)
    
    for mes in numeros_mes:
        contador = 0
        for item in legit_por_mes:
            if item['mes'] == mes:
                valoresl.append(item['count'])
                contador = 1
        if contador == 0:
            valoresf.append(0)
    
    drawing5 = Drawing(ancho_grafico, alto_grafico)
    data = [valoresl, valoresf]
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.width = 300
    chart.height = 100
    chart.data = data
    chart.categoryAxis.categoryNames = [str(h) for h in numeros_mes]
    chart.bars[0].fillColor = HexColor("#FF0000")  # Color para la categoría "Legit"
    chart.bars[1].fillColor = HexColor("#00FF00")  # Color para la categoría "Fraud"

    x = ancho_grafico * 2
    
    drawing5.add(chart)
    drawing5.drawOn(c, x, y)
    
    c.showPage()
    c.save()
    
    with open('reporteria/graficos.pdf', 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="graficos.pdf"'

    return response