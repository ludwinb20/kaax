from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from kaax_app import soporte

scheduler = BackgroundScheduler()

# Programa la tarea que se ejecutará cada minuto
scheduler.add_job(
    func=soporte.renovartoken,
    trigger=IntervalTrigger(minutes=1),
    next_run_time=datetime.now(tz=pytz.timezone('America/Tegucigalpa'))
)

# Programa la tarea que se ejecutará cada 10 minutos
scheduler.add_job(
    func=soporte.entrenar,
    trigger=IntervalTrigger(minutes=1),
    next_run_time=datetime.now(tz=pytz.timezone('America/Tegucigalpa'))
)

scheduler.start()

