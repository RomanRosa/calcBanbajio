# app/manual_analysis.py
"""
Módulo de Análisis Manual

Contiene las funciones necesarias para procesar archivos de OCTUBRE,
realizar cálculos financieros, clasificar discrepancias y reordenar
columnas de salida según los requerimientos establecidos.
"""

import os
import pandas as pd
import numpy as np
import numpy_financial as npf  # Para otros cálculos financieros

# =============================================================================
# Función para clasificar discrepancias (utilizada para cada métrica)
# =============================================================================
def clasificar_discrepancia(row):
    """
    Clasifica la discrepancia basada en los valores del sistema versus la calculadora.

    Args:
        row (pd.Series): Fila del DataFrame con 'valor_sistema', 'valor_calculadora' y 'Saldo Total'.

    Returns:
        tuple: (grado_discrepancia, tipo_impacto, impacto_financiero, clasificacion_impacto)
    """
    valor_sistema = row['valor_sistema']
    valor_calculadora = row['valor_calculadora']
    saldo_total = row['Saldo Total']
    
    # Evitar división por cero
    if valor_calculadora != 0:
        diff_pct = ((valor_sistema - valor_calculadora) / valor_calculadora) * 100
    else:
        diff_pct = 0

    diff_abs = abs(diff_pct)
    
    # A) Grado de discrepancia
    if diff_abs >= 5:
        grado = "Significativa"
    elif diff_abs < 4:
        grado = "No significativa"
    else:
        grado = "Moderada"
    
    # B) Tipo de impacto (severidad)
    if diff_pct < 0:
        if diff_abs > 10:
            severidad = "Alta"
        elif diff_abs >= 5:
            severidad = "Media"
        else:
            severidad = "Baja"
    else:
        if diff_abs > 5:
            severidad = "Alta"
        elif diff_abs >= 2.5:
            severidad = "Media"
        else:
            severidad = "Baja"
    
    # C) Impacto financiero (% sobre el saldo total)
    if saldo_total != 0:
        impacto_pct = (abs(valor_sistema - valor_calculadora) / saldo_total) * 100
    else:
        impacto_pct = 0
        
    if impacto_pct > 15:
        imp_fin = "Alta"
    elif impacto_pct >= 5:
        imp_fin = "Media"
    else:
        imp_fin = "Baja"
    
    # D) Clasificación del impacto financiero
    if impacto_pct > 15:
        clasif_imp = "Alta"
    elif impacto_pct >= 5:
        clasif_imp = "Media"
    else:
        clasif_imp = "Baja"
    
    return (grado, severidad, imp_fin, clasif_imp)

# =============================================================================
# Función auxiliar para aplicar la clasificación a cada métrica
# =============================================================================
def aplicar_clasificacion(df, metric_name, sistema_col, calculadora_col):
    """
    Aplica la función de clasificación a cada fila de las columnas indicadas y
    agrega las nuevas columnas resultantes al DataFrame.
    """
    temp = df[[sistema_col, calculadora_col, 'Saldo Total']].copy()
    # Renombrar columnas para homogeneizar nombres
    temp = temp.rename(columns={sistema_col: 'valor_sistema', calculadora_col: 'valor_calculadora'})
    clasificaciones = temp.apply(clasificar_discrepancia, axis=1)
    df[f"{metric_name}.grado de discrepancia"] = clasificaciones.apply(lambda x: x[0])
    df[f"{metric_name}.tipo de impacto (severidad)"] = clasificaciones.apply(lambda x: x[1])
    df[f"{metric_name}.impacto financiero"] = clasificaciones.apply(lambda x: x[2])
    df[f"{metric_name}.clasificación del impacto financiero"] = clasificaciones.apply(lambda x: x[3])

# =============================================================================
# Función auxiliar para agregar columnas "placeholder" vacías
# =============================================================================
def agregar_columnas_placeholder(df, prefix, placeholders):
    """
    Agrega al DataFrame columnas vacías con el prefijo y nombre de placeholder definidos.
    
    Args:
        df (pd.DataFrame): DataFrame a modificar.
        prefix (str): Prefijo que se usará en el nombre de la columna.
        placeholders (list): Lista de nombres base para las columnas.
    """
    for ph in placeholders:
        col_name = f"{ph}-{prefix.upper()}"
        df[col_name] = ""

# =============================================================================
# Función auxiliar para calcular y clasificar la desviación estándar
# =============================================================================
def agregar_desviacion_estandar(df, grupo, col_sistema, col_calculadora):
    """
    Calcula la desviación estándar (std = |x1 - x2| / 2) para cada fila y la clasifica
    en "Baja", "Media" o "Alta" según el porcentaje relativo al promedio de ambos valores.
    
    Args:
        df (pd.DataFrame): DataFrame con las columnas de comparación.
        grupo (str): Identificador del grupo (ej. "SC", "IO", etc.).
        col_sistema (str): Nombre de la columna del valor del sistema.
        col_calculadora (str): Nombre de la columna del valor de la calculadora.
    """
    desv = abs(df[col_sistema] - df[col_calculadora]) / 2
    df[f"Desviación Estandar {grupo.upper()}"] = desv
    promedio = (df[col_sistema] + df[col_calculadora]) / 2
    porcentaje = np.where(promedio != 0, (desv / abs(promedio)) * 100, 0)
    condiciones = [porcentaje < 5, (porcentaje >= 5) & (porcentaje < 15), porcentaje >= 15]
    elecciones = ["Baja", "Media", "Alta"]
    df[f"Clasificación Desviación {grupo.upper()}"] = np.select(condiciones, elecciones, default="Baja")

# =============================================================================
# Función principal: Procesa archivos de OCTUBRE y retorna el DataFrame final
# =============================================================================
def process_octubre(cuentas_path='/content/CUENTAS_OCTUBRE.xlsx',
                    movimientos_path='/content/MOVIMIENTOS_OCTUBRE.xlsx',
                    promociones_path='/content/PROMOCIONES_OCTUBRE.xlsx'):
    """
    Procesa los archivos de cuentas, movimientos y promociones de OCTUBRE y realiza
    cálculos financieros y clasificaciones, retornando el DataFrame final con todas las columnas
    organizadas según lo solicitado.
    
    Args:
        cuentas_path (str): Ruta del archivo de cuentas.
        movimientos_path (str): Ruta del archivo de movimientos.
        promociones_path (str): Ruta del archivo de promociones.
    
    Returns:
        pd.DataFrame: DataFrame final con los cálculos y clasificaciones.
    """
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    
    # Cargar archivos y homogeneizar nombres de columnas
    cuentas_oct = pd.read_excel(cuentas_path)
    cuentas_oct.columns = cuentas_oct.columns.str.lower()

    mov_oct = pd.read_excel(movimientos_path)
    mov_oct.columns = mov_oct.columns.str.lower()

    promo_oct = pd.read_excel(promociones_path)
    promo_oct.columns = promo_oct.columns.str.lower()

    cuentas_oct['id'] = cuentas_oct['id'].astype(str).str.strip()
    mov_oct['id'] = mov_oct['id'].astype(str).str.strip()
    promo_oct['id'] = promo_oct['id'].astype(str).str.strip()
    promo_oct['tipo_promo'] = promo_oct['tipo_promo'].astype(str).str.strip()

    promo_oct = promo_oct.drop_duplicates(subset='id', keep='first')
    cuentas_oct['mes'] = 'Occtubre'

    # Última transacción por ID
    mov_oct_last = mov_oct.groupby('id', as_index=False)['fecha_transaccion'].max()
    mov_oct_last.rename(columns={'fecha_transaccion': 'fecha última transacción'}, inplace=True)
    
    # Merge de cuentas con la última transacción
    df_oct = pd.merge(cuentas_oct, mov_oct_last, on='id', how='left')
    df_oct = pd.merge(df_oct, promo_oct, on='id', how='left', suffixes=("", "_promo"))
    tipo_promo_map = promo_oct.set_index('id')['tipo_promo']
    df_oct['tipo_promo'] = df_oct['id'].map(tipo_promo_map)
    
    # Preparar la descripción en mayúsculas para identificar tipos en movimientos
    mov_oct['descripcion_upper'] = mov_oct['descripcion'].fillna('').str.upper()
    
    # Funciones locales para identificar cargos e intereses
    def fn_compras_otros_cargos(row):
        return row['monto_facturacion'] if 'COMISIÓN POR PENALIZACIÓN' in row['descripcion_upper'] else 0

    def fn_interes_a_cargo(row):
        return row['monto_facturacion'] if row['descripcion_upper'].startswith('INTERES SOBRE COMPRA') else 0

    def fn_iva_isr(row):
        return row['monto_facturacion'] if row['descripcion_upper'].startswith('IVA SOBRE COMISION') else 0

    mov_oct['compras_otros_cargos'] = mov_oct.apply(fn_compras_otros_cargos, axis=1)
    mov_oct['interes_a_cargo'] = mov_oct.apply(fn_interes_a_cargo, axis=1)
    mov_oct['iva_isr'] = mov_oct.apply(fn_iva_isr, axis=1)
    
    # Agregación de movimientos por ID
    agg_dict = {
        'compras_otros_cargos': 'sum',
        'interes_a_cargo': 'sum',
        'iva_isr': 'sum'
    }
    group_vars = mov_oct.groupby('id', as_index=False).agg(agg_dict)
    df_oct = pd.merge(df_oct, group_vars, on='id', how='left')
    for col in ['compras_otros_cargos', 'interes_a_cargo', 'iva_isr']:
        df_oct[col] = df_oct[col].fillna(0)
    
    # Cálculos de días y subtotales
    df_oct['número de días del ciclo'] = (df_oct['fecha_limite'] - df_oct['fecha_corte']).dt.days + 1
    df_oct['periodo de la promoción'] = df_oct['número de días del ciclo']
    df_oct['subtotal_sin_iva'] = df_oct['saldo_inicial'] + df_oct['compras_otros_cargos'] + df_oct['interes_a_cargo']
    df_oct['subtotal_con_iva'] = df_oct['subtotal_sin_iva'] + df_oct['iva_isr']
    df_oct['pagos_depositos_interes_bruto'] = df_oct['subtotal_con_iva'] - df_oct['saldo_cierre']
    
    df_oct['saldocorte.valor de la calculadora'] = df_oct['subtotal_con_iva'] - df_oct['pagos_depositos_interes_bruto']
    df_oct['saldocorte.valor del sistema'] = df_oct['saldo_cierre']
    df_oct['saldocorte.diferencia absoluta'] = abs(df_oct['saldocorte.valor del sistema'] - df_oct['saldocorte.valor de la calculadora'])
    df_oct['saldocorte.diferencia porcentual'] = np.where(
        df_oct['saldocorte.valor del sistema'] != 0,
        (df_oct['saldocorte.diferencia absoluta'] / abs(df_oct['saldocorte.valor del sistema'])) * 100,
        0
    )
    
    # Cálculo de tasas e interés ordinario
    def get_tasa(perfil):
        perfil = str(perfil).lower()
        if 'employee benefits' in perfil:
            return 0.26
        elif 'visa básica' in perfil:
            return 0.65
        elif 'visa platinum' in perfil:
            return 0.349
        elif 'visa clásica' in perfil:
            return 0.60
        elif 'visa oro' in perfil:
            return 0.50
        elif 'visa infinite' in perfil:
            return 0.305
        else:
            return 0

    df_oct['tasa anual'] = df_oct['perfil_interes'].apply(get_tasa)
    df_oct['tasa diaria'] = df_oct['tasa anual'] / 360
    df_oct['interesordinario.valor de la calculadora'] = (
        (((abs(df_oct['saldo_inicial']) + abs(df_oct['saldo_cierre'])) / 2) + abs(df_oct['pago_nogen_int']))
        * df_oct['tasa diaria']
        * df_oct['número de días del ciclo']
    )
    df_oct['interesordinario.valor del sistema'] = np.nan  # A determinar por el sistema
    df_oct['interesordinario.diferencia absoluta'] = abs(df_oct['interesordinario.valor del sistema'] - df_oct['interesordinario.valor de la calculadora'])
    df_oct['interesordinario.diferencia porcentual'] = np.where(
        df_oct['interesordinario.valor de la calculadora'] != 0,
        (df_oct['interesordinario.diferencia absoluta'] / abs(df_oct['interesordinario.valor de la calculadora'])) * 100,
        0
    )
    
    # Cálculo de interés en promociones con interés
    df_oct['interespromosconinteres.valor del sistema'] = df_oct['interes_total']
    df_oct['interespromosconinteres.valor de la calculadora'] = (
        abs(df_oct['monto_total']) *
        ((df_oct['tasa_interes'] / 100) / 360) *
        (df_oct['periodo de la promoción'] + 1)
    )
    df_oct['interespromosconinteres.diferencia absoluta'] = abs(
        df_oct['interespromosconinteres.valor del sistema'] - df_oct['interespromosconinteres.valor de la calculadora']
    )
    df_oct['interespromosconinteres.diferencia porcentual'] = np.where(
        df_oct['interespromosconinteres.valor del sistema'] != 0,
        (df_oct['interespromosconinteres.diferencia absoluta'] / abs(df_oct['interespromosconinteres.valor del sistema'])) * 100,
        0
    )
    
    # Cálculos para saldo de cierre de mes
    df_oct['saldocierremes.valor del sistema'] = df_oct['saldo_cierre']
    df_oct['saldocierremes.valor de la calculadora'] = df_oct['saldo_cierre']
    df_oct['saldocierremes.diferencia absoluta'] = 0
    df_oct['saldocierremes.diferencia porcentual'] = 0
    
    # Cálculo de pago para no generar intereses
    def calcular_pago_nogen(row):
        if pd.notnull(row.get('tipo_promo')):
            promo_type = str(row.get('tipo_promo')).lower()
            if promo_type in ['msi', 'mci']:
                if 'sin intereses' in promo_type:
                    saldo_promo = -row['monto_total'] * 0.3126
                else:
                    saldo_promo = -row['monto_total'] * ((row['numero_de_pagos'] - 1.0) / row['numero_de_pagos'])
                return row['saldo_cierre'] - saldo_promo
        return row['saldo_cierre']
    
    df_oct['pagonogenintereses.valor de la calculadora'] = df_oct.apply(calcular_pago_nogen, axis=1)
    df_oct['pagonogenintereses.valor del sistema'] = df_oct['pago_nogen_int']
    df_oct['pagonogenintereses.diferencia absoluta'] = abs(
        df_oct['pagonogenintereses.valor del sistema'] - df_oct['pagonogenintereses.valor de la calculadora']
    )
    df_oct['pagonogenintereses.diferencia porcentual'] = np.where(
        df_oct['pagonogenintereses.valor del sistema'] != 0,
        (df_oct['pagonogenintereses.diferencia absoluta'] / abs(df_oct['pagonogenintereses.valor del sistema'])) * 100,
        0
    )
    
    # Cálculo de pago mínimo
    def calcular_pago_minimo(row):
        tipo = str(row['tipo']).upper()
        if 'TOTALERO' in tipo:
            if abs(row['pago_minimo']) <= (row['limite_credito'] * 0.0125):
                return -row['limite_credito'] * 0.0125
            else:
                return -abs(row['saldo_cierre']) * 0.2210
        else:
            return -max(
                row['limite_credito'] * 0.0125,
                abs(row['saldo_cierre']) * 0.05,
                (abs(row['saldo_cierre']) * 0.015) * 0.015
            )
    
    df_oct['pagominimo.valor de la calculadora'] = df_oct.apply(calcular_pago_minimo, axis=1)
    df_oct['pagominimo.valor del sistema'] = df_oct['pago_minimo']
    df_oct['pagominimo.diferencia absoluta'] = abs(
        df_oct['pagominimo.valor del sistema'] - df_oct['pagominimo.valor de la calculadora']
    )
    df_oct['pagominimo.diferencia porcentual'] = np.where(
        df_oct['pagominimo.valor del sistema'] != 0,
        (df_oct['pagominimo.diferencia absoluta'] / abs(df_oct['pagominimo.valor del sistema'])) * 100,
        0
    )
    
    # Cálculos de intereses a favor
    df_oct['saldo_favor'] = df_oct['saldo_inicial'].apply(lambda x: x if x > 0 else 0)
    df_oct['tasa_decimal'] = df_oct['tasa_interes'].fillna(0) / 100.0
    df_oct['dias_calculo'] = (df_oct['fecha_corte'] - df_oct['fecha última transacción']).dt.days + 1
    df_oct['interesesafavor.valor de la calculadora'] = np.round(
        df_oct['saldo_favor'] * (df_oct['tasa_decimal'] / 360) * df_oct['dias_calculo'],
        2
    )
    df_oct['interesesafavor.valor del sistema'] = df_oct['saldo_favor']
    df_oct['interesesafavor.diferencia absoluta'] = abs(
        df_oct['interesesafavor.valor del sistema'] - df_oct['interesesafavor.valor de la calculadora']
    )
    df_oct['interesesafavor.diferencia porcentual'] = np.where(
        df_oct['interesesafavor.valor del sistema'] != 0,
        (df_oct['interesesafavor.diferencia absoluta'] / abs(df_oct['interesesafavor.valor del sistema'])) * 100,
        0
    )
    
    # Cálculos de CAT
    df_oct['cat.valor del sistema'] = df_oct.get('cat_sistema', np.nan)
    def calcular_cat_calculadora(row):
        net_cashflows = [-1000, 200, 300, 400, 500] 
        tir_periodo = npf.irr(net_cashflows)
        if pd.isna(tir_periodo) or tir_periodo is None:
            return np.nan
        n = 12
        tir_anual_simple = tir_periodo * n
        return tir_anual_simple * 100
    df_oct['cat.valor de la calculadora'] = df_oct.apply(calcular_cat_calculadora, axis=1)
    df_oct['cat.diferencia absoluta'] = abs(df_oct['cat.valor del sistema'] - df_oct['cat.valor de la calculadora'])
    df_oct['cat.diferencia porcentual'] = np.where(
        df_oct['cat.valor del sistema'] != 0,
        (df_oct['cat.diferencia absoluta'] / abs(df_oct['cat.valor del sistema'])) * 100,
        0
    )
    
    # Rellenar valores nulos
    df_oct = df_oct.fillna(0)
    
    # Renombrar columnas para salida final
    df_final = df_oct.copy()
    df_final = df_final.rename(columns={
        'producto': 'Producto',
        'id': 'ID Cliente',
        'tipo': 'Tipo de Cliente',
        'mes': 'Mes',
        'limite_credito': 'Límite de Crédito del Producto',
        'saldo_cierre': 'Saldo Total',
        'tasa_interes': 'Tasa Interés',
        'tipo_promo': 'Tipo de Promo',
        'periodo de la promoción': 'Periodo de la Promoción',
        'número de días del ciclo': 'Número de Días del Ciclo',
        'fecha_corte': 'Fecha de Corte',
        'fecha última transacción': 'Fecha Última Transacción',
        'compras_otros_cargos': 'Compras y Otros Cargos',
        'interes_a_cargo': 'Interés a Cargo',
        'iva_isr': 'IVA/ISR',
        'subtotal_sin_iva': 'SubTotal Sin IVA',
        'subtotal_con_iva': 'SubTotal Con IVA',
        'pagos_depositos_interes_bruto': 'Pagos y Depósitos e Interés Bruto'
    })
    
    df_final = df_final.rename(columns={
        'saldocorte.valor del sistema': 'Valor del Sistema SC',
        'saldocorte.valor de la calculadora': 'Valor de la Calculadora SC',
        'saldocorte.diferencia absoluta': 'Diferencia Absoluta SC',
        'saldocorte.diferencia porcentual': 'Diferencia Porcentual SC'
    })
    df_final = df_final.rename(columns={
        'interesordinario.valor del sistema': 'Valor del Sistema IO',
        'interesordinario.valor de la calculadora': 'Valor de la Calculadora IO',
        'interesordinario.diferencia absoluta': 'Diferencia Absoluta IO',
        'interesordinario.diferencia porcentual': 'Diferencia Porcentual IO'
    })
    df_final = df_final.rename(columns={
        'interespromosconinteres.valor del sistema': 'Valor del Sistema IP',
        'interespromosconinteres.valor de la calculadora': 'Valor de la Calculadora IP',
        'interespromosconinteres.diferencia absoluta': 'Diferencia Absoluta IP',
        'interespromosconinteres.diferencia porcentual': 'Diferencia Porcentual IP'
    })
    df_final = df_final.rename(columns={
        'saldocierremes.valor del sistema': 'Valor del Sistema SCM',
        'saldocierremes.valor de la calculadora': 'Valor de la Calculadora SCM',
        'saldocierremes.diferencia absoluta': 'Diferencia Absoluta SCM',
        'saldocierremes.diferencia porcentual': 'Diferencia Porcentual SCM'
    })
    df_final = df_final.rename(columns={
        'pagonogenintereses.valor del sistema': 'Valor del Sistema PGNI',
        'pagonogenintereses.valor de la calculadora': 'Valor de la Calculadora PGNI',
        'pagonogenintereses.diferencia absoluta': 'Diferencia Absoluta PGNI',
        'pagonogenintereses.diferencia porcentual': 'Diferencia Porcentual PGNI'
    })
    df_final = df_final.rename(columns={
        'pagominimo.valor del sistema': 'Valor del Sistema PM',
        'pagominimo.valor de la calculadora': 'Valor de la Calculadora PM',
        'pagominimo.diferencia absoluta': 'Diferencia Absoluta PM',
        'pagominimo.diferencia porcentual': 'Diferencia Porcentual PM'
    })
    df_final = df_final.rename(columns={
        'interesesafavor.valor del sistema': 'Valor del Sistema IF',
        'interesesafavor.valor de la calculadora': 'Valor de la Calculadora IF',
        'interesesafavor.diferencia absoluta': 'Diferencia Absoluta IF',
        'interesesafavor.diferencia porcentual': 'Diferencia Porcentual IF'
    })
    df_final = df_final.rename(columns={
        'cat.valor del sistema': 'Valor del Sistema CAT',
        'cat.valor de la calculadora': 'Valor de la Calculadora CAT',
        'cat.diferencia absoluta': 'Diferencia Absoluta CAT',
        'cat.diferencia porcentual': 'Diferencia Porcentual CAT'
    })
    
    # ----------------------------------------------------------------------------
    # Agregar columnas de clasificación para cada métrica
    # ----------------------------------------------------------------------------
    aplicar_clasificacion(df_final, 'saldocorte', 'Valor del Sistema SC', 'Valor de la Calculadora SC')
    aplicar_clasificacion(df_final, 'interesordinario', 'Valor del Sistema IO', 'Valor de la Calculadora IO')
    aplicar_clasificacion(df_final, 'interespromosconinteres', 'Valor del Sistema IP', 'Valor de la Calculadora IP')
    aplicar_clasificacion(df_final, 'saldocierremes', 'Valor del Sistema SCM', 'Valor de la Calculadora SCM')
    aplicar_clasificacion(df_final, 'pagonogenintereses', 'Valor del Sistema PGNI', 'Valor de la Calculadora PGNI')
    aplicar_clasificacion(df_final, 'pagominimo', 'Valor del Sistema PM', 'Valor de la Calculadora PM')
    aplicar_clasificacion(df_final, 'interesesafavor', 'Valor del Sistema IF', 'Valor de la Calculadora IF')
    aplicar_clasificacion(df_final, 'cat', 'Valor del Sistema CAT', 'Valor de la Calculadora CAT')
    
    # Renombrar columnas de clasificación para cada grupo
    df_final = df_final.rename(columns={
        'saldocorte.grado de discrepancia': 'Grado de Discrepancia SC',
        'saldocorte.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) SC',
        'saldocorte.impacto financiero': 'Impacto Financiero SC',
        'saldocorte.clasificación del impacto financiero': 'Clasificación del Impacto Financiero SC',
        'interesordinario.grado de discrepancia': 'Grado de Discrepancia IO',
        'interesordinario.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) IO',
        'interesordinario.impacto financiero': 'Impacto Financiero IO',
        'interesordinario.clasificación del impacto financiero': 'Clasificación del Impacto Financiero IO',
        'interespromosconinteres.grado de discrepancia': 'Grado de Discrepancia IP',
        'interespromosconinteres.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) IP',
        'interespromosconinteres.impacto financiero': 'Impacto Financiero IP',
        'interespromosconinteres.clasificación del impacto financiero': 'Clasificación del Impacto Financiero IP',
        'saldocierremes.grado de discrepancia': 'Grado de Discrepancia SCM',
        'saldocierremes.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) SCM',
        'saldocierremes.impacto financiero': 'Impacto Financiero SCM',
        'saldocierremes.clasificación del impacto financiero': 'Clasificación del Impacto Financiero SCM',
        'pagonogenintereses.grado de discrepancia': 'Grado de Discrepancia PGNI',
        'pagonogenintereses.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) PGNI',
        'pagonogenintereses.impacto financiero': 'Impacto Financiero PGNI',
        'pagonogenintereses.clasificación del impacto financiero': 'Clasificación del Impacto Financiero PGNI',
        'pagominimo.grado de discrepancia': 'Grado de Discrepancia PM',
        'pagominimo.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) PM',
        'pagominimo.impacto financiero': 'Impacto Financiero PM',
        'pagominimo.clasificación del impacto financiero': 'Clasificación del Impacto Financiero PM',
        'interesesafavor.grado de discrepancia': 'Grado de Discrepancia IF',
        'interesesafavor.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) IF',
        'interesesafavor.impacto financiero': 'Impacto Financiero IF',
        'interesesafavor.clasificación del impacto financiero': 'Clasificación del Impacto Financiero IF',
        'cat.grado de discrepancia': 'Grado de Discrepancia CAT',
        'cat.tipo de impacto (severidad)': 'Tipo de Impacto (Severidad) CAT',
        'cat.impacto financiero': 'Impacto Financiero CAT',
        'cat.clasificación del impacto financiero': 'Clasificación del Impacto Financiero CAT'
    })
    
    # ----------------------------------------------------------------------------
    # Agregar columnas de DESVIACIÓN ESTÁNDAR para cada métrica
    # ----------------------------------------------------------------------------
    agregar_desviacion_estandar(df_final, "SC", "Valor del Sistema SC", "Valor de la Calculadora SC")
    agregar_desviacion_estandar(df_final, "IO", "Valor del Sistema IO", "Valor de la Calculadora IO")
    agregar_desviacion_estandar(df_final, "IP", "Valor del Sistema IP", "Valor de la Calculadora IP")
    agregar_desviacion_estandar(df_final, "SCM", "Valor del Sistema SCM", "Valor de la Calculadora SCM")
    agregar_desviacion_estandar(df_final, "PGNI", "Valor del Sistema PGNI", "Valor de la Calculadora PGNI")
    agregar_desviacion_estandar(df_final, "PM", "Valor del Sistema PM", "Valor de la Calculadora PM")
    agregar_desviacion_estandar(df_final, "IF", "Valor del Sistema IF", "Valor de la Calculadora IF")
    agregar_desviacion_estandar(df_final, "CAT", "Valor del Sistema CAT", "Valor de la Calculadora CAT")
    
    # ----------------------------------------------------------------------------
    # Reordenar columnas según el orden final solicitado
    # ----------------------------------------------------------------------------
    final_columns = [
        "Producto", "ID Cliente", "Tipo de Cliente", "Mes",
        "Límite de Crédito del Producto", "Saldo Total", "Tasa Interés",
        "Tipo de Promo", "Periodo de la Promoción", "Compras y Otros Cargos",
        "Número de Días del Ciclo", "Fecha de Corte", "Fecha Última Transacción",
        "Interés a Cargo", "IVA/ISR", "SubTotal Sin IVA", "SubTotal Con IVA",
        "Pagos y Depósitos e Interés Bruto",
        # Saldo al Corte (SC)
        "Valor del Sistema SC", "Valor de la Calculadora SC", "Diferencia Absoluta SC", "Diferencia Porcentual SC",
        "Grado de Discrepancia SC", "Tipo de Impacto (Severidad) SC", "Impacto Financiero SC",
        "Clasificación del Impacto Financiero SC", "Desviación Estandar SC", "Clasificación Desviación SC",
        "A1-SC", "A2-SC", "A3-SC", "B1-SC", "B2-SC", "B3-SC", "Cálculo SC", "Comparativa SC",
        # Interés Ordinario (IO)
        "Valor del Sistema IO", "Valor de la Calculadora IO", "Diferencia Absoluta IO", "Diferencia Porcentual IO",
        "Grado de Discrepancia IO", "Tipo de Impacto (Severidad) IO", "Impacto Financiero IO",
        "Clasificación del Impacto Financiero IO", "Desviación Estandar IO", "Clasificación Desviación IO",
        "A1-IO", "A2-IO", "A3-IO", "B1-IO", "B2-IO", "B3-IO", "Cálculo IO", "Comparativa IO",
        # Interés Promos Con Interés (IP)
        "Valor del Sistema IP", "Valor de la Calculadora IP", "Diferencia Absoluta IP", "Diferencia Porcentual IP",
        "Grado de Discrepancia IP", "Tipo de Impacto (Severidad) IP", "Impacto Financiero IP",
        "Clasificación del Impacto Financiero IP", "Desviación Estandar IP", "Clasificación Desviación IP",
        "A1-IP", "A2-IP", "A3-IP", "B1-IP", "B2-IP", "B3-IP", "Cálculo IP", "Comparativa IP",
        # Saldo al Cierre de Mes (SCM)
        "Valor del Sistema SCM", "Valor de la Calculadora SCM", "Diferencia Absoluta SCM", "Diferencia Porcentual SCM",
        "Grado de Discrepancia SCM", "Tipo de Impacto (Severidad) SCM", "Impacto Financiero SCM",
        "Clasificación del Impacto Financiero SCM", "Desviación Estandar SCM", "Clasificación Desviación SCM",
        "A1-SCM", "A2-SCM", "A3-SCM", "B1-SCM", "B2-SCM", "B3-SCM", "Cálculo SCM", "Comparativa SCM",
        # Pago para No Generar Intereses (PGNI)
        "Valor del Sistema PGNI", "Valor de la Calculadora PGNI", "Diferencia Absoluta PGNI", "Diferencia Porcentual PGNI",
        "Grado de Discrepancia PGNI", "Tipo de Impacto (Severidad) PGNI", "Impacto Financiero PGNI",
        "Clasificación del Impacto Financiero PGNI", "Desviación Estandar PGNI", "Clasificación Desviación PGNI",
        "A1-PGNI", "A2-PGNI", "A3-PGNI", "B1-PGNI", "B2-PGNI", "B3-PGNI", "Cálculo PGNI", "Comparativa PGNI",
        # Pago Mínimo (PM)
        "Valor del Sistema PM", "Valor de la Calculadora PM", "Diferencia Absoluta PM", "Diferencia Porcentual PM",
        "Grado de Discrepancia PM", "Tipo de Impacto (Severidad) PM", "Impacto Financiero PM",
        "Clasificación del Impacto Financiero PM", "Desviación Estandar PM", "Clasificación Desviación PM",
        "A1-PM", "A2-PM", "A3-PM", "B1-PM", "B2-PM", "B3-PM", "Cálculo PM", "Comparativa PM",
        # Intereses a Favor (IF)
        "Valor del Sistema IF", "Valor de la Calculadora IF", "Diferencia Absoluta IF", "Diferencia Porcentual IF",
        "Grado de Discrepancia IF", "Tipo de Impacto (Severidad) IF", "Impacto Financiero IF",
        "Clasificación del Impacto Financiero IF", "Desviación Estandar IF", "Clasificación Desviación IF",
        "A1-IF", "A2-IF", "A3-IF", "B1-IF", "B2-IF", "B3-IF", "Cálculo IF", "Comparativa IF",
        # CAT
        "Valor del Sistema CAT", "Valor de la Calculadora CAT", "Diferencia Absoluta CAT", "Diferencia Porcentual CAT",
        "Grado de Discrepancia CAT", "Tipo de Impacto (Severidad) CAT", "Impacto Financiero CAT",
        "Clasificación del Impacto Financiero CAT", "Desviación Estandar CAT", "Clasificación Desviación CAT",
        "A1-CAT", "A2-CAT", "A3-CAT", "B1-CAT", "B2-CAT", "B3-CAT", "Cálculo CAT", "Comparativa CAT"
    ]
    
    # Asegurar que todas las columnas estén presentes
    for col in final_columns:
        if col not in df_final.columns:
            df_final[col] = ""
    
    df_final = df_final.reindex(columns=final_columns)
    
    return df_final

# =============================================================================
# Ejecución independiente (para pruebas)
# =============================================================================
if __name__ == '__main__':
    df_final = process_octubre(cuentas_path='CUENTAS_OCTUBRE.xlsx',
                               movimientos_path='MOVIMIENTOS_OCTUBRE.xlsx',
                               promociones_path='PROMOCIONES_OCTUBRE.xlsx')
    print("DataFrame final (primeras 10 filas):")
    print(df_final.head(10))
