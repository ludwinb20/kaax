# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from . import soporte

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=soporte.renovartoken, # reemplaza "tu_funcion_a_ejecutar" por el nombre de tu función
        trigger='interval',
        minutes=180,
        next_run_time=datetime.now(tz=pytz.timezone('America/Tegucigalpa')) # cambia la zona horaria si es necesario
    )

    scheduler.add_job(
        func=soporte.entrenar, # reemplaza "tu_funcion_a_ejecutar" por el nombre de tu función
        trigger='interval',
        days=1,
        next_run_time=datetime.now(tz=pytz.timezone('America/Tegucigalpa')) # cambia la zona horaria si es necesario
    )

    scheduler.start()
