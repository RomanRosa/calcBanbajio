# app/calc_tools.py
"""
Módulo de Herramientas y Análisis Financiero

Este módulo agrupa dos grandes conjuntos de funcionalidades:
  1. Herramientas estadísticas para el análisis de datos de tarjetas de crédito,
     mediante la clase CreditCardStats.
  2. Funcionalidades para cálculos financieros, incluyendo:
       - Cálculo de interés utilizando convenciones de 365 y 360 días (clases
         FinancialCalculationPRIME y FinancialCalculationPRIME360).
       - Funcionalidades adicionales en la clase Calculadora para distintos
         indicadores financieros.

Este módulo también incluye constantes utilizadas para evitar la duplicación
de nombres de columnas y para mantener consistencia en los análisis.
"""

import pandas as pd
import numpy as np
from scipy import stats as spystats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import optimize

# =============================================================================
# Constantes para nombres de columnas (para evitar duplicación de cadenas)
# =============================================================================
SALDO_AL_CORTE = "Saldo al Corte"
SALDO_ANTERIOR = "Saldo Anterior"
COMPRAS_Y_OTROS_CARGOS = "Compras y Otros Cargos"
PAGOS_Y_DEPOSITOS = "Pagos y Depositos"
INTERES = "Interes"
IVA_INTERES = "IVA Interes"
PAGO_MINIMO = "Pago Minimo"
PAGO_SIN_INTERESES = "Pago Sin Intereses"
TASA_ANUAL = "Tasa Anual"
MONTO = "Monto"
FECHA_INICIO = "Fecha Inicio"
FECHA_FIN = "Fecha Fin"
SALDO_INSOLUTO = "Saldo Insoluto (MXN)"
COMISIONES_APLICADAS = "Comisiones Aplicadas (MXN)"

# =============================================================================
# Clase para análisis estadístico de datos de tarjetas de crédito
# =============================================================================
class CreditCardStats:
    def __init__(self, dataframe: pd.DataFrame):
        """
        Inicializa la clase con un DataFrame para realizar análisis estadístico.

        Args:
            dataframe (pd.DataFrame): DataFrame con los datos a analizar.
        """
        self.df = dataframe

    def describe_data(self) -> pd.DataFrame:
        """Retorna un resumen estadístico de los datos numéricos."""
        return self.df.describe()

    def variance(self, column: str) -> float:
        """Calcula la varianza de la columna especificada."""
        return self.df[column].var()

    def standard_deviation(self, column: str) -> float:
        """Calcula la desviación estándar de la columna especificada."""
        return self.df[column].std()

    def correlation_matrix(self) -> pd.DataFrame:
        """Retorna la matriz de correlación entre las variables numéricas."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        return numeric_df.corr()

    def hypothesis_test_mean(self, column: str, population_mean: float) -> dict:
        """
        Realiza una prueba t de una muestra para comparar la media muestral con la media poblacional.

        Args:
            column (str): Nombre de la columna.
            population_mean (float): Valor de la media poblacional.

        Returns:
            dict: Diccionario con T-Statistic, P-Value, Sample Mean y Population Mean.
        """
        sample_mean = self.df[column].mean()
        t_statistic, p_value = spystats.ttest_1samp(self.df[column].dropna(), population_mean)
        return {
            "T-Statistic": t_statistic,
            "P-Value": p_value,
            "Sample Mean": sample_mean,
            "Population Mean": population_mean
        }

    def confidence_interval(self, column: str, confidence: float = 0.95) -> dict:
        """
        Calcula el intervalo de confianza para la media de la columna especificada.

        Args:
            column (str): Nombre de la columna.
            confidence (float): Nivel de confianza (por defecto 0.95).

        Returns:
            dict: Contiene la media y el intervalo de confianza.
        """
        data = self.df[column].dropna()
        mean = np.mean(data)
        sem = spystats.sem(data)
        interval = spystats.t.interval(confidence, len(data) - 1, loc=mean, scale=sem)
        return {
            "Mean": mean,
            "Confidence Interval": interval
        }

    def data_completeness(self) -> pd.Series:
        """
        Calcula el porcentaje de datos no nulos en cada columna.

        Returns:
            pd.Series: Porcentaje de completitud de datos por columna.
        """
        return self.df.notnull().mean() * 100

    def data_dispersion(self, column: str) -> dict:
        """
        Calcula el rango y el rango intercuartílico (IQR) para la columna especificada.

        Args:
            column (str): Nombre de la columna.

        Returns:
            dict: Contiene 'Range' y 'Interquartile Range (IQR)'.
        """
        data_range = self.df[column].max() - self.df[column].min()
        iqr = spystats.iqr(self.df[column].dropna())
        return {
            "Range": data_range,
            "Interquartile Range (IQR)": iqr
        }

    def test_normality(self, column: str) -> dict:
        """
        Realiza la prueba de Shapiro-Wilk para evaluar la normalidad de la distribución de la columna.

        Args:
            column (str): Nombre de la columna.

        Returns:
            dict: Contiene la estadística, el P-Value y si se asume normalidad.
        """
        stat, p_value = spystats.shapiro(self.df[column].dropna())
        return {
            "Statistic": stat,
            "P-Value": p_value,
            "Is Normal": p_value > 0.05
        }

    def correlation_test(self, column1: str, column2: str) -> dict:
        """
        Calcula el coeficiente de correlación de Pearson entre dos columnas.

        Args:
            column1 (str): Nombre de la primera columna.
            column2 (str): Nombre de la segunda columna.

        Returns:
            dict: Contiene el coeficiente de correlación y el P-Value.
        """
        correlation, p_value = spystats.pearsonr(
            self.df[column1].dropna(),
            self.df[column2].dropna()
        )
        return {
            "Correlation": correlation,
            "P-Value": p_value
        }

# =============================================================================
# Clases para Cálculos Financieros con Convenciones de 365 y 360 días
# =============================================================================
class FinancialCalculationPRIME:
    def __init__(self, data):
        """
        Inicializa la clase con un DataFrame o una ruta a un archivo CSV.

        Args:
            data (pd.DataFrame or str): DataFrame con los datos o ruta a un archivo CSV.
        """
        if isinstance(data, pd.DataFrame):
            self.dataset = data.copy()
        elif isinstance(data, str):
            self.dataset = pd.read_csv(data)
        else:
            raise ValueError("El parámetro 'data' debe ser un DataFrame o una ruta a un archivo CSV.")

    def calculate_interest(self, row, start_date_col: str, end_date_col: str, principal_col: str, annual_rate_col: str) -> float:
        """
        Calcula el interés utilizando la convención de 365 días.

        Args:
            row (pd.Series): Fila del DataFrame.
            start_date_col (str): Nombre de la columna con la fecha de inicio.
            end_date_col (str): Nombre de la columna con la fecha final.
            principal_col (str): Nombre de la columna con el monto principal.
            annual_rate_col (str): Nombre de la columna con la tasa anual.

        Returns:
            float: Interés calculado.
        """
        start_date = pd.to_datetime(row[start_date_col])
        end_date = pd.to_datetime(row[end_date_col])
        days = (end_date - start_date).days
        annual_rate = row[annual_rate_col]
        daily_rate = annual_rate / 365
        principal = row[principal_col]
        return round(days * daily_rate * principal, 2)

    def process_dataset(self):
        """
        Procesa el DataFrame añadiendo columnas de interés, saldo al corte,
        IVA y pago mínimo.

        Los cálculos se realizan según las fórmulas establecidas.
        """
        self.dataset["Interes"] = self.dataset.apply(
            lambda row: self.calculate_interest(row, FECHA_INICIO, FECHA_FIN, MONTO, TASA_ANUAL),
            axis=1
        )
        self.dataset[SALDO_AL_CORTE] = (
            self.dataset[SALDO_ANTERIOR] +
            self.dataset[COMPRAS_Y_OTROS_CARGOS] -
            self.dataset[PAGOS_Y_DEPOSITOS] +
            self.dataset["Interes"]
        ).round(2)
        self.dataset[IVA_INTERES] = (self.dataset["Interes"] * 0.16).round(2)
        self.dataset[PAGO_MINIMO] = (
            (self.dataset[SALDO_AL_CORTE] * 0.10) +
            self.dataset["Interes"] +
            self.dataset[IVA_INTERES]
        ).round(2)
        self.dataset[PAGO_SIN_INTERESES] = (
            self.dataset[SALDO_AL_CORTE] - self.dataset["Interes"]
        ).round(2)

    def validate_prime_rules(self):
        """
        Valida que los cálculos realizados cumplan con las reglas definidas para PRIME.
        Imprime discrepancias encontradas.
        """
        discrepancies = []
        for idx, row in self.dataset.iterrows():
            calculated_interest = self.calculate_interest(row, FECHA_INICIO, FECHA_FIN, MONTO, TASA_ANUAL)
            if round(row["Interes"], 2) != calculated_interest:
                discrepancies.append(f"Fila {idx}: Diferencia en cálculo de interés")
            expected_saldo = round(
                row[SALDO_ANTERIOR] +
                row[COMPRAS_Y_OTROS_CARGOS] -
                row[PAGOS_Y_DEPOSITOS] +
                row["Interes"], 2
            )
            if round(row[SALDO_AL_CORTE], 2) != expected_saldo:
                discrepancies.append(f"Fila {idx}: Diferencia en cálculo de {SALDO_AL_CORTE}")
        if discrepancies:
            print("Discrepancias encontradas:")
            for d in discrepancies:
                print(d)
        else:
            print("Todos los cálculos cumplen con PRIME.")

    def save_results(self, output_path: str):
        """
        Guarda el DataFrame procesado en un archivo CSV.

        Args:
            output_path (str): Ruta donde se guardará el archivo CSV.
        """
        self.dataset.to_csv(output_path, index=False)
        print(f"Resultados guardados en: {output_path}")

class FinancialCalculationPRIME360(FinancialCalculationPRIME):
    def calculate_interest(self, row, start_date_col: str, end_date_col: str, principal_col: str, annual_rate_col: str) -> float:
        """
        Calcula el interés utilizando la convención de 360 días.

        Los argumentos son iguales que en FinancialCalculationPRIME.
        """
        start_date = pd.to_datetime(row[start_date_col])
        end_date = pd.to_datetime(row[end_date_col])
        days = (end_date - start_date).days
        annual_rate = row[annual_rate_col]
        daily_rate = annual_rate / 360
        principal = row[principal_col]
        return round(days * daily_rate * principal, 2)

# =============================================================================
# Clase Calculadora: Cálculos Adicionales Basados en Datos CSV
# =============================================================================
class Calculadora:
    def __init__(self, archivo: str):
        """
        Inicializa la Calculadora leyendo un archivo CSV.

        Args:
            archivo (str): Ruta del archivo CSV con los datos.
        """
        self.data = pd.read_csv(archivo)

    def saldo_al_corte(self) -> float:
        """
        Calcula el saldo al corte sumando y restando diversos componentes financieros.

        Returns:
            float: Saldo al corte calculado.
        """
        saldo_anterior = self.data['Saldo anterior'].sum()
        compras_cargos = self.data['Compras y otros cargos'].sum()
        interes_cargo = self.data['Interés a cargo'].sum()
        pagos_depositos = self.data['Pagos y depósitos'].sum()
        interes_bruto = self.data['Interés bruto'].sum()
        iva_isr = self.data['IVA/ISR'].sum()
        saldo_corte = saldo_anterior + compras_cargos + interes_cargo - pagos_depositos - interes_bruto + iva_isr
        return round(saldo_corte, 2)

    def interes_ordinario(self, tasa_anual: float, dias_credito: int) -> float:
        """
        Calcula el interés ordinario basado en el saldo promedio diario y la tasa anual.

        Args:
            tasa_anual (float): Tasa anual aplicada.
            dias_credito (int): Número de días de crédito.

        Returns:
            float: Interés ordinario calculado.
        """
        saldo_promedio = self.data['Saldo promedio diario'].sum()
        interes_diario = tasa_anual / 360
        interes = saldo_promedio * interes_diario * (dias_credito + 1)
        return round(interes, 2)

    def interes_promocional(self, tasa_promo: float, dias_promo: int) -> float:
        """
        Calcula el interés promocional.

        Args:
            tasa_promo (float): Tasa promocional aplicada.
            dias_promo (int): Número de días de promoción.

        Returns:
            float: Interés promocional calculado.
        """
        saldo_promo = self.data['Saldo promoción'].sum()
        interes_diario = tasa_promo / 360
        interes = saldo_promo * interes_diario * (dias_promo + 1)
        return round(interes, 2)

    def saldo_cierre_mes(self) -> float:
        """
        Calcula el saldo al cierre de mes considerando movimientos y transacciones fuera de horario.

        Returns:
            float: Saldo al cierre de mes calculado.
        """
        saldo_inicial = self.data['Saldo inicial'].sum()
        compras = self.data['Compras'].sum()
        intereses = self.data['Intereses'].sum()
        comisiones = self.data['Comisiones'].sum()
        pagos = self.data['Pagos'].sum()
        ultimo_dia = datetime.now().replace(day=1) - timedelta(days=1)
        limite_corte = datetime.combine(ultimo_dia, datetime.min.time()).replace(hour=22)
        transac_fuera = self.data[(self.data['Fecha'] >= limite_corte) & (self.data['Fecha'] < ultimo_dia)]
        saldo_cierre = saldo_inicial + compras + intereses + comisiones - pagos + transac_fuera['Monto'].sum()
        return round(saldo_cierre, 2)

    def pago_no_interes(self) -> float:
        """
        Calcula el pago necesario para no generar intereses.

        Returns:
            float: Pago para no generar intereses.
        """
        saldo_cierre = self.saldo_cierre_mes()
        saldo_promo = self.data['Saldo promoción sin interés'].sum()
        interes_promo = self.interes_promocional(0.01, 30)
        parcialidad_promo = self.data['Parcialidad promoción'].sum()
        monto_vencido_promo = self.data['Monto vencido promoción'].sum()
        sobregiro_promo = self.data['Sobregiro de promo'].sum()
        iva = self.data['IVA'].sum()
        pago_no_int = saldo_cierre - (saldo_promo + interes_promo) + parcialidad_promo + monto_vencido_promo + sobregiro_promo + iva
        return round(pago_no_int, 2)

    def pago_minimo(self, limite_credito: float) -> float:
        """
        Calcula el pago mínimo basado en tres escenarios y selecciona el de mayor valor absoluto.

        Args:
            limite_credito (float): Límite de crédito del producto.

        Returns:
            float: Pago mínimo calculado.
        """
        saldo_final = self.saldo_cierre_mes()
        sobregiro = self.data['Sobregiro'].sum()
        saldo_promo = self.data['Saldo promoción'].sum()
        interes_cargo = self.data['Interés a cargo'].sum()
        iva_isr = self.data['IVA/ISR'].sum()
        opcion1 = limite_credito * 0.0125
        opcion2 = (saldo_final - sobregiro - saldo_promo) * 0.05 + saldo_promo * 0.05
        opcion3 = (saldo_final - sobregiro - saldo_promo) * 0.015 + interes_cargo + iva_isr
        pago_min = max(opcion1, opcion2, opcion3)
        return round(pago_min, 2)

    def interes_favor(self, tasa_anual: float, dias_favor: int) -> float:
        """
        Calcula los intereses a favor en caso de ajustes manuales.

        Args:
            tasa_anual (float): Tasa anual aplicada.
            dias_favor (int): Número de días para el cálculo.

        Returns:
            float: Intereses a favor calculados.
        """
        saldo_favor = self.data['Saldo a favor'].sum()
        interes_diario = tasa_anual / 360
        interes = saldo_favor * interes_diario * dias_favor
        return round(interes, 2)

    def tasa_anual_total(self) -> float:
        """
        Calcula el CAT (Costo Anual Total) utilizando una TIR estimada.

        Returns:
            float: CAT en porcentaje.
        """
        flujos = [-self.saldo_cierre_mes()]
        fechas = [datetime.now()]
        for _, row in self.data.iterrows():
            flujos.append(row['Pagos'])
            fechas.append(row['Fecha'])
        # Usamos un método numérico para calcular la TIR
        tir = optimize.newton(
            lambda r: sum([f / (1 + r) ** ((date - fechas[0]).days / 365) for f, date in zip(flujos, fechas)]),
            0.01
        )
        # Convertir a una tasa anual compuesta (aproximación para 12 meses)
        cat = (1 + tir) ** 11
        return round(cat * 100, 2)

# =============================================================================
# Bloque de Ejecución para Pruebas (si se ejecuta el módulo de forma independiente)
# =============================================================================
if __name__ == "__main__":
    # Ejemplo de uso para FinancialCalculationPRIME y PRIME360
    input_file = "path_to_dataset.csv"
    output_file = "resultados_calculados_prime.csv"
    output_file_360 = "resultados_calculados_prime_360.csv"

    print("Procesando cálculos con FinancialCalculationPRIME...")
    financial_calc = FinancialCalculationPRIME(input_file)
    financial_calc.process_dataset()
    financial_calc.validate_prime_rules()
    financial_calc.save_results(output_file)

    print("Procesando cálculos con FinancialCalculationPRIME360...")
    financial_calc_360 = FinancialCalculationPRIME360(input_file)
    financial_calc_360.process_dataset()
    financial_calc_360.validate_prime_rules()
    financial_calc_360.save_results(output_file_360)

    # Ejemplo de uso para la clase Calculadora
    calc = Calculadora('datos.csv')
    print(f"Saldo al corte: {calc.saldo_al_corte()}")
    print(f"Interés ordinario: {calc.interes_ordinario(0.3, 30)}")
    print(f"Interés promocional: {calc.interes_promocional(0.1, 15)}")
    print(f"Saldo al cierre de mes: {calc.saldo_cierre_mes()}")
    print(f"Pago para no generar intereses: {calc.pago_no_interes()}")
    print(f"Pago mínimo: {calc.pago_minimo(50000)}")
    print(f"Intereses a favor: {calc.interes_favor(0.05, 10)}")
    print(f"CAT: {calc.tasa_anual_total()}%")
