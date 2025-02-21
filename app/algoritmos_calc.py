# app/algoritmos_calc.py
"""
Módulo de Algoritmos de Cálculos Financieros

Este módulo contiene:
  1. La clase DBConnector, encargada de conectarse a la base de datos PostgreSQL.
  2. La clase Algoritmos, que expone métodos para calcular diversas métricas financieras,
     tales como:
       - INTERÉS ORDINARIO
       - SALDO AL CIERRE DE MES
       - PAGO PARA NO GENERAR INTERESES
       - PAGO MÍNIMO
       - SALDO AL CORTE
       - INTERÉS DE PROMOCIONES
       - INTERÉS A FAVOR

Cada método acepta un parámetro opcional 'id' para filtrar los resultados para un único registro
o para todos.
"""

import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# -----------------------------------------------------------------------------
# Clase DBConnector: Conexión a la Base de Datos
# -----------------------------------------------------------------------------
class DBConnector:
    """
    Clase para la conexión a la base de datos PostgreSQL.

    Utiliza psycopg2 para la conexión directa y SQLAlchemy para ejecutar consultas
    y obtener resultados en DataFrames.
    """
    def __init__(self):
        self.dbname = os.getenv("DB_NAME_APP", "visa_db")
        self.user = os.getenv("DB_USER_APP", "app_admin")
        self.password = os.getenv("DB_PASSWORD_APP", "app_secure_password")
        self.host = os.getenv("DB_HOST_APP", "localhost")
        self.port = os.getenv("DB_PORT_APP", "5432")
        self.connection = None
        self.engine = None
        self.connect()

    def connect(self):
        """
        Establece la conexión a la base de datos y crea el engine de SQLAlchemy.
        """
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.engine = create_engine(
                f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
            )
        except Exception as e:
            print("Error al conectar a la base de datos:", e)

    def close(self):
        """
        Cierra la conexión a la base de datos.
        """
        if self.connection:
            self.connection.close()

    def run_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y retorna el resultado en un DataFrame.

        Args:
            query (str): La consulta SQL a ejecutar.
            params (dict, optional): Parámetros para la consulta.

        Returns:
            pd.DataFrame: DataFrame con el resultado de la consulta.
        """
        try:
            df = pd.read_sql_query(text(query), self.engine, params=params)
            return df
        except Exception as e:
            print("Error ejecutando la consulta:", e)
            return None

# -----------------------------------------------------------------------------
# Clase Algoritmos: Cálculos Financieros mediante Consultas SQL
# -----------------------------------------------------------------------------
class Algoritmos:
    """
    Clase que contiene métodos para calcular diferentes métricas financieras
    utilizando datos de las tablas de cuentas, movimientos y promociones.
    """
    def __init__(self, db_connector: DBConnector):
        self.db = db_connector

    def get_interes_ordinario(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el INTERÉS ORDINARIO para cuentas de octubre.

        Se realiza el cálculo basado en:
          - Saldo inicial y saldo de cierre.
          - Pago que no genera intereses.
          - Tasa anual asignada según el perfil de interés.
          - Número de días de crédito.

        Args:
            id (int, optional): Si se especifica, filtra el cálculo para ese ID.

        Returns:
            pd.DataFrame: DataFrame con las columnas originales y el cálculo del interés ordinario.
        """
        filter_clause = "WHERE id = :id" if id is not None else ""
        params = {'id': id} if id is not None else {}
        query = f"""
        WITH cte AS (
            SELECT
                id,
                saldo_inicial,
                saldo_cierre,
                pago_nogen_int,
                fecha_corte,
                fecha_limite,
                producto,
                perfil_interes,
                CASE 
                    WHEN perfil_interes ILIKE '%Employee Benefits%' THEN 0.26
                    WHEN perfil_interes ILIKE '%Visa Básica%' THEN 0.65
                    WHEN perfil_interes ILIKE '%Visa Platinum%' THEN 0.349
                    WHEN perfil_interes ILIKE '%Visa Clásica%' THEN 0.60
                    WHEN perfil_interes ILIKE '%Visa Oro%' THEN 0.50
                    WHEN perfil_interes ILIKE '%Visa Infinite%' THEN 0.305
                    ELSE 0
                END AS tasa_anual
            FROM cuentas_octubre
            {filter_clause}
        )
        SELECT
            id,
            saldo_inicial,
            saldo_cierre,
            pago_nogen_int,
            fecha_corte,
            fecha_limite,
            producto,
            perfil_interes,
            tasa_anual,
            tasa_anual / 360 AS tasa_diaria,
            (ABS(saldo_inicial) + ABS(saldo_cierre)) / 2 AS saldo_promedio_diario,
            ((ABS(saldo_inicial) + ABS(saldo_cierre)) / 2) + ABS(pago_nogen_int) AS saldo_promedio_ajustado,
            (fecha_limite - fecha_corte) + 1 AS dias_credito,
            (
                (((ABS(saldo_inicial) + ABS(saldo_cierre)) / 2) + ABS(pago_nogen_int))
                * (tasa_anual / 360)
                * ((fecha_limite - fecha_corte) + 1)
            ) AS interes_ordinario
        FROM cte;
        """
        return self.db.run_query(query, params)

    def get_saldo_cierre_mes(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el SALDO AL CIERRE DE MES para cuentas de octubre.

        Se obtienen los valores de:
          - Compras y otros cargos.
          - Interés a cargo y IVA/ISR.
          - Subtotal sin y con IVA.
          - Diferencias entre el saldo reportado y calculado.

        Args:
            id (int, optional): Si se especifica, filtra el cálculo para ese ID.

        Returns:
            pd.DataFrame: DataFrame con el cálculo del saldo al cierre de mes.
        """
        filter_clause = "WHERE c.id = :id" if id is not None else ""
        params = {'id': id} if id is not None else {}
        query = f"""
        WITH mov AS (
           SELECT 
              c.id,
              c.saldo_inicial,
              c.saldo_cierre,
              COALESCE(SUM(CASE WHEN m.descripcion ILIKE '%COMISIÓN POR PENALIZACIÓN%' THEN m.monto_facturacion ELSE 0 END), 0) AS compras_otros_cargos,
              COALESCE(SUM(CASE WHEN m.descripcion ILIKE 'INTERES SOBRE COMPRA%%' THEN m.monto_facturacion ELSE 0 END), 0) AS interes_a_cargo,
              COALESCE(SUM(CASE WHEN m.descripcion ILIKE 'IVA SOBRE COMISION%%' THEN m.monto_facturacion ELSE 0 END), 0) AS iva_isr
           FROM cuentas_octubre c
           LEFT JOIN movimientos_octubre m ON c.id = m.id
           {filter_clause}
           GROUP BY c.id, c.saldo_inicial, c.saldo_cierre
        )
        SELECT 
           id,
           saldo_inicial,
           saldo_cierre AS saldo_cierre_reportado,
           compras_otros_cargos,
           interes_a_cargo,
           iva_isr,
           (saldo_inicial + (compras_otros_cargos + interes_a_cargo)) AS subtotal_sin_iva,
           ((saldo_inicial + (compras_otros_cargos + interes_a_cargo)) + iva_isr) AS subtotal_con_iva,
           (((saldo_inicial + (compras_otros_cargos + interes_a_cargo)) + iva_isr) - saldo_cierre) AS pagos_depositos_interes_bruto,
           saldo_cierre AS saldo_al_corte_calculado,
           (saldo_cierre - ABS(((saldo_inicial + (compras_otros_cargos + interes_a_cargo)) + iva_isr) - saldo_cierre)) AS diferencia,
           ABS(((saldo_inicial + (compras_otros_cargos + interes_a_cargo)) + iva_isr) - saldo_cierre) AS saldo_al_corte_absoluto,
           CASE WHEN saldo_cierre <> 0 THEN ((saldo_cierre - ABS(((saldo_inicial + (compras_otros_cargos + interes_a_cargo)) + iva_isr) - saldo_cierre)) / saldo_cierre::numeric * 100)
                ELSE 0 END AS diferencia_porcentual
        FROM mov;
        """
        return self.db.run_query(query, params)

    def get_pago_no_genera_intereses(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el PAGO PARA NO GENERAR INTERESES para cuentas de octubre.

        La fórmula se basa en:
          Pago = Saldo_Cierre - (SaldoPromo + InteresPromo) + ParcialidadPromo + Monto_Vencido

        Args:
            id (int, optional): Si se especifica, filtra el cálculo para ese ID.

        Returns:
            pd.DataFrame: DataFrame con los valores calculados y diferencias.
        """
        filter_clause = "WHERE p.id = :id" if id is not None else ""
        params = {'id': id} if id is not None else {}
        query = f"""
        WITH cuenta AS (
          SELECT 
            id,
            saldo_inicial,
            saldo_cierre,
            pago_nogen_int
          FROM cuentas_octubre
          { "WHERE id = :id" if id is not None else "" }
        ),
        promo AS (
          SELECT 
            id,
            monto_total,
            parcialidad,
            monto_pendiente
          FROM promociones_octubre
          { "WHERE id = :id" if id is not None else "" }
          LIMIT 1
        )
        SELECT 
          c.id,
          c.saldo_inicial,
          c.saldo_cierre AS saldo_cierre_reportado,
          (-1 * p.monto_total) AS saldo_promo,
          p.parcialidad AS parcialidad_promo,
          p.monto_pendiente AS monto_vencido_promo,
          0.00 AS sobregiro_promo,
          0.00 AS iva_promo,
          (c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente) AS pago_nogen_int_calculado,
          c.pago_nogen_int AS pago_nogen_int_reportado,
          ABS((c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente) - c.pago_nogen_int) AS diferencia,
          ABS(c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente) AS saldo_al_corte_absoluto,
          CASE 
            WHEN (c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente) <> 0 
              THEN (ABS((c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente) - c.pago_nogen_int)
                    / ABS(c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente)) * 100
            ELSE 0 
          END AS diferencia_porcentual,
          CASE 
            WHEN ROUND(ABS(c.saldo_cierre - (-1 * p.monto_total) + p.parcialidad + p.monto_pendiente), 2)
                 = ROUND(ABS(c.pago_nogen_int), 2)
            THEN 'SI'
            ELSE 'NO'
          END AS coincide
        FROM cuenta c
        CROSS JOIN promo p;
        """
        return self.db.run_query(query, params)

    def get_pago_minimo(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el PAGO MÍNIMO para cuentas de octubre evaluando tres escenarios y
        selecciona el de mayor valor absoluto.

        Args:
            id (int, optional): Si se especifica, filtra el cálculo para ese ID.

        Returns:
            pd.DataFrame: DataFrame con el cálculo del pago mínimo, diferencias y validación de la fórmula teórica.
        """
        filter_clause = "WHERE p.id = :id" if id is not None else ""
        params = {'id': id} if id is not None else {}
        query = f"""
        WITH DatosPrincipales AS (
            SELECT 
                p.id,
                p.secuencia_corte,
                p.monto_original,
                p.monto_total,
                p.monto_pendiente AS saldo_promo,
                p.interes_total AS interes_cargo,
                p.parcialidad,
                p.tasa_interes,
                p.tipo_promo,
                c.limite_credito,
                c.saldo_cierre AS saldo_final,
                c.pago_minimo AS pago_minimo_registrado
            FROM promociones_octubre p
            JOIN cuentas_octubre c ON p.id = c.id
            {filter_clause}
        ),
        CalculoPagos AS (
            SELECT 
                *,
                ROUND((limite_credito * 0.0125)::numeric, 2) AS pago1,
                ROUND(((saldo_final - saldo_promo) * 0.05 + parcialidad * 0.05)::numeric, 2) AS pago2,
                ROUND(
                    (((saldo_final - saldo_promo) * 0.015 + interes_cargo) * 0.015 + interes_cargo)::numeric, 2
                ) AS pago3
            FROM DatosPrincipales
        )
        SELECT 
            id,
            secuencia_corte,
            monto_original,
            monto_total,
            saldo_promo,
            interes_cargo,
            parcialidad,
            tasa_interes,
            tipo_promo,
            limite_credito,
            saldo_final,
            pago_minimo_registrado,
            pago1,
            pago2,
            pago3,
            CASE 
                WHEN ABS(pago1) >= ABS(pago2) AND ABS(pago1) >= ABS(pago3) THEN pago1
                WHEN ABS(pago2) >= ABS(pago3) THEN pago2
                ELSE pago3
            END AS pago_minimo_teorico,
            -1 * GREATEST(
                limite_credito * 0.0125,
                ABS(saldo_final) * 0.05,
                (ABS(saldo_final) * 0.015) * 0.015
            ) AS pago_minimo_calculado,
            ROUND(( -1 * GREATEST(
                limite_credito * 0.0125,
                ABS(saldo_final) * 0.05,
                (ABS(saldo_final) * 0.015) * 0.015
            ) - pago_minimo_registrado)::numeric, 2) AS diferencia,
            ROUND(ABS(-1 * GREATEST(
                limite_credito * 0.0125,
                ABS(saldo_final) * 0.05,
                (ABS(saldo_final) * 0.015) * 0.015
            ) - pago_minimo_registrado)::numeric, 2) AS diferencia_absoluta,
            ROUND((CASE 
                WHEN ABS(-1 * GREATEST(
                    limite_credito * 0.0125,
                    ABS(saldo_final) * 0.05,
                    (ABS(saldo_final) * 0.015) * 0.015
                ) - pago_minimo_registrado) <> 0 
                THEN (ABS(-1 * GREATEST(
                    limite_credito * 0.0125,
                    ABS(saldo_final) * 0.05,
                    (ABS(saldo_final) * 0.015) * 0.015
                ) - pago_minimo_registrado) / ABS(-1 * GREATEST(
                    limite_credito * 0.0125,
                    ABS(saldo_final) * 0.05,
                    (ABS(saldo_final) * 0.015) * 0.015
                )) * 100
                ELSE 0 
            END)::numeric, 2) AS diferencia_porcentual,
            CASE 
                WHEN ROUND(ABS(-1 * GREATEST(
                    limite_credito * 0.0125,
                    ABS(saldo_final) * 0.05,
                    (ABS(saldo_final) * 0.015) * 0.015
                )), 2) = ROUND(ABS(pago_minimo_registrado), 2)
                THEN 'SI'
                ELSE 'NO'
            END AS coincide_formula_teorica
        FROM CalculoPagos;
        """
        return self.db.run_query(query, params)

    def get_saldo_al_corte(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el SALDO AL CORTE para cuentas de octubre.

        Se utiliza para explorar la estructura de la tabla y confirmar sus columnas.

        Args:
            id (int, optional): Si se especifica, filtra el resultado por ese ID.

        Returns:
            pd.DataFrame: Una muestra (10 filas) de la tabla cuentas_octubre.
        """
        filter_clause = "WHERE id = :id" if id is not None else ""
        params = {'id': id} if id is not None else {}
        query = f"SELECT * FROM cuentas_octubre {filter_clause} LIMIT 10;"
        return self.db.run_query(query, params)

    def get_interes_promocional(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el INTERÉS DE PROMOCIONES para cuentas de octubre.

        Args:
            id (int, optional): Si se especifica, filtra el cálculo para ese ID.

        Returns:
            pd.DataFrame: DataFrame con el cálculo del interés promocional.
        """
        filter_clause = "WHERE p.id = :desired_id" if id is not None else ""
        params = {'desired_id': id} if id is not None else {}
        query = f"""
        WITH promo AS (
            SELECT DISTINCT
                p.id,
                p.monto_original,
                p.tasa_interes,
                m.fecha_transaccion,
                c.fecha_corte,
                ABS(p.monto_original) AS saldo_promocion,
                (p.tasa_interes / 100.0) AS tasa_decimal,
                (c.fecha_corte - m.fecha_transaccion) + 1 AS dias_promocion
            FROM promociones_octubre p
            JOIN movimientos_octubre m ON p.id = m.id
            JOIN cuentas_octubre c ON p.id = c.id
            {filter_clause}
        )
        SELECT
            id,
            monto_original AS saldo_inicial,
            tasa_interes,
            fecha_transaccion,
            fecha_corte,
            saldo_promocion,
            tasa_decimal,
            dias_promocion,
            ROUND(
                saldo_promocion * (tasa_decimal / 360) * dias_promocion,
                2
            ) AS interes_promocional
        FROM promo
        ORDER BY fecha_transaccion;
        """
        return self.db.run_query(query, params)

    def get_interes_a_favor(self, id: int = None) -> pd.DataFrame:
        """
        Calcula el INTERÉS A FAVOR para cuentas de octubre.

        Args:
            id (int, optional): Si se especifica, filtra el cálculo para ese ID.

        Returns:
            pd.DataFrame: DataFrame con el cálculo del interés a favor.
        """
        filter_clause = "WHERE p.id = :desired_id" if id is not None else ""
        params = {'desired_id': id} if id is not None else {}
        query = f"""
        WITH datos_promociones AS (
            SELECT DISTINCT
                p.id,
                p.monto_original,
                p.tasa_interes,
                m.fecha_transaccion,
                c.fecha_corte,
                c.saldo_inicial,
                (c.fecha_corte - m.fecha_transaccion) + 1 AS dias_calculo,
                COALESCE(p.tasa_interes, 0) / 100.0 AS tasa_decimal,
                CASE 
                    WHEN c.saldo_inicial > 0 THEN c.saldo_inicial 
                    ELSE 0 
                END AS saldo_favor
            FROM promociones_octubre p
            JOIN movimientos_octubre m ON p.id = m.id
            JOIN cuentas_octubre c ON p.id = c.id
            {filter_clause}
            GROUP BY 
                p.id,
                p.monto_original,
                p.tasa_interes,
                m.fecha_transaccion,
                c.fecha_corte,
                c.saldo_inicial
        )
        SELECT 
            id,
            fecha_transaccion,
            fecha_corte,
            dias_calculo,
            tasa_interes,
            saldo_inicial,
            saldo_favor,
            ROUND(
                saldo_favor * (tasa_decimal / 360) * dias_calculo,
                2
            ) AS interes_a_favor
        FROM datos_promociones
        ORDER BY fecha_transaccion;
        """
        df = self.db.run_query(query, params)
        if df is not None:
            print("\nDesglose de Interés a Favor por registro:")
            for _, row in df.iterrows():
                print(f"\nFecha Transacción: {row['fecha_transaccion']}")
                print(f"Días considerados: {row['dias_calculo']}")
                print(f"Saldo inicial: ${row['saldo_inicial']:,.2f}")
                print(f"Saldo a favor: ${row['saldo_favor']:,.2f}")
                print(f"Tasa aplicada: {row['tasa_interes']}%")
                print(f"Interés a favor: ${row['interes_a_favor']:,.2f}")
        return df
