from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
EXCEL_PATH = 'data.xlsx'

def load_data():
    if os.path.exists(EXCEL_PATH):
        return pd.read_excel(EXCEL_PATH)
    else:
        return pd.DataFrame(columns=[
            "fecha_creacion", "fecha_examen_solicitado", "area", "caso", "folio",
            "rut_paciente", "nombre_paciente", "fecha_cuestionario_medico_realizado",
            "fecha_examen_realizado", "fecha_facturado", "estado",
            "direccion_paciente", "crea_solicitud"
        ])

def save_data(df):
    df.to_excel(EXCEL_PATH, index=False)

def generar_recomendacion(estado):
    if pd.isna(estado):
        return "Estado vacío: requiere revisión manual"
    estado = estado.upper()
    if "NO CONTACTO" in estado:
        return "Intentar nuevo contacto en próximo horario disponible"
    elif "RECHAZA" in estado:
        return "Registrar rechazo formal y cerrar caso"
    elif "DUPLICADO" in estado:
        return "Evitar duplicación, mantener solo un folio activo"
    elif "EXITOSO" in estado:
        return "Caso finalizado correctamente, no requiere acción"
    else:
        return "Revisar manualmente por profesional clínico"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        return redirect(url_for('welcome', email=email))
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    email = request.args.get('email', '')
    return render_template('welcome.html', email=email)

@app.route('/add', methods=['GET', 'POST'])
def add_case():
    if request.method == 'POST':
        df = load_data()
        new_case = {
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_examen_solicitado": request.form.get("fecha_examen_solicitado"),
            "area": request.form.get("area"),
            "caso": request.form.get("caso"),
            "folio": request.form.get("folio"),
            "rut_paciente": request.form.get("rut_paciente"),
            "nombre_paciente": request.form.get("nombre_paciente"),
            "fecha_cuestionario_medico_realizado": request.form.get("fecha_cuestionario_medico_realizado"),
            "fecha_examen_realizado": request.form.get("fecha_examen_realizado"),
            "fecha_facturado": request.form.get("fecha_facturado"),
            "estado": request.form.get("estado"),
            "direccion_paciente": request.form.get("direccion_paciente"),
            "crea_solicitud": request.form.get("crea_solicitud")
        }
        df = df.append(new_case, ignore_index=True)
        save_data(df)
        return redirect(url_for('welcome', email=request.args.get('email')))
    return render_template('add_case.html')

@app.route('/view', methods=['GET', 'POST'])
def view_case():
    case = None
    recomendacion = None
    if request.method == 'POST':
        case_id = request.form['caso']
        df = load_data()
        resultado = df[df['caso'].astype(str) == str(case_id)]
        if not resultado.empty:
            case = resultado.to_dict('records')
            recomendacion = generar_recomendacion(case[0].get("estado", ""))
    return render_template('view_case.html', case=case, recomendacion=recomendacion)

@app.route('/all')
def all_cases():
    df = load_data()
    return render_template('all_cases.html', cases=df.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)
