# app/calculos.py
"""
Módulo de Cálculos Financieros

Contiene la clase BanBajioCalculator, encargada de realizar:
  1. Cálculo de Intereses Promocionales.
  2. Cálculo del Saldo al Cierre de Mes (calculado) y sus diferencias.
  3. Cálculo del Pago para No Generar Intereses.
  4. Cálculo del Pago Mínimo, evaluando tres escenarios y seleccionando el de mayor valor absoluto.

La clase utiliza DataFrames de Pandas con los datos de promociones, movimientos y cuentas.
"""

import pandas as pd
import numpy as np
import numpy_financial as npf  # Para cálculos financieros (irr, etc.)

class BanBajioCalculator:
    def __init__(self, promos_octubre: pd.DataFrame, movimientos_octubre: pd.DataFrame, cuentas_octubre: pd.DataFrame):
        """
        Constructor de la clase.

        Args:
            promos_octubre (pd.DataFrame): DataFrame con información de promociones (columnas ejemplo:
                [ID, SECUENCIA_CORTE, MONTO_ORIGINAL, MONTO_TOTAL, MONTO_PENDIENTE, INTERES_TOTAL,
                 PARCIALIDAD, TASA_INTERES, TIPO_PROMO, ...]).
            movimientos_octubre (pd.DataFrame): DataFrame con información de movimientos (ej.: [ID, FECHA_TRANSACCION,
                MONTO_FACTURACION, CODIGO, ...]).
            cuentas_octubre (pd.DataFrame): DataFrame con información de cuentas (ej.: [ID, FECHA_CORTE, SALDO_INICIAL,
                PAGOS_TOTALES, SALDO_CIERRE, PAGO_MINIMO, LIMITE_CREDITO, MONTO_VENCIDO, ...]).
        """
        # Se copian los DataFrames para evitar modificaciones externas
        self.promos_octubre = promos_octubre.copy()
        self.movimientos_octubre = movimientos_octubre.copy()
        self.cuentas_octubre = cuentas_octubre.copy()
        
        # Convertir a datetime las columnas de fecha si aún no lo están
        if 'FECHA_TRANSACCION' in self.movimientos_octubre.columns:
            if not pd.api.types.is_datetime64_any_dtype(self.movimientos_octubre['FECHA_TRANSACCION']):
                self.movimientos_octubre['FECHA_TRANSACCION'] = pd.to_datetime(self.movimientos_octubre['FECHA_TRANSACCION'])
        if 'FECHA_CORTE' in self.cuentas_octubre.columns:
            if not pd.api.types.is_datetime64_any_dtype(self.cuentas_octubre['FECHA_CORTE']):
                self.cuentas_octubre['FECHA_CORTE'] = pd.to_datetime(self.cuentas_octubre['FECHA_CORTE'])

    # -------------------------------------------------------------------------
    # CÁLCULO DE INTERESES PROMOCIONALES
    # -------------------------------------------------------------------------
    def _obtener_min_fecha_transaccion(self) -> pd.DataFrame:
        """
        Obtiene la fecha mínima de transacción para cada ID en movimientos_octubre.

        Returns:
            pd.DataFrame: DataFrame con columnas [ID, Min_Fecha_Transaccion].
        """
        min_fecha_df = (
            self.movimientos_octubre
            .groupby('ID', as_index=False)
            .agg(Min_Fecha_Transaccion=('FECHA_TRANSACCION', 'min'))
        )
        return min_fecha_df

    def _merge_tablas_promos(self) -> pd.DataFrame:
        """
        Realiza el merge de promos_octubre con:
          - La fecha mínima de transacción.
          - La FECHA_CORTE de cuentas_octubre.

        Returns:
            pd.DataFrame: DataFrame combinado con las columnas necesarias para el cálculo de intereses promocionales.
        """
        min_fecha_df = self._obtener_min_fecha_transaccion()
        df_merged = pd.merge(self.promos_octubre, min_fecha_df, how='left', on='ID')
        df_merged = pd.merge(df_merged, self.cuentas_octubre[['ID', 'FECHA_CORTE']], how='left', on='ID')
        return df_merged

    def _calcular_interes_promocional(self, row) -> float:
        """
        Calcula el interés promocional para una fila determinada utilizando la fórmula:
            Interés = SaldoPromocion * (TasaPromo / 360) * (DiasPromo + 1)
        Con la excepción de promociones "Totalero" con saldo 0 (interés = 0).

        Args:
            row (pd.Series): Fila con columnas requeridas: [TIPO_PROMO, MONTO_PENDIENTE, TASA_INTERES, Dias_Promocion].

        Returns:
            float: Valor del Interés Promocional.
        """
        tipo_promo = row['TIPO_PROMO']
        saldo_promocion = row['MONTO_PENDIENTE']
        tasa_promo = row['TASA_INTERES']
        dias_promo = row['Dias_Promocion']
        
        tasa_promo = 0.0 if pd.isna(tasa_promo) else tasa_promo
        saldo_promocion = 0.0 if pd.isna(saldo_promocion) else saldo_promocion
        dias_promo = 0 if pd.isna(dias_promo) else dias_promo

        if tipo_promo == "Totalero" and saldo_promocion == 0:
            return 0.0
        
        interes = saldo_promocion * (tasa_promo / 360.0) * (dias_promo + 1)
        return interes

    def calcular_intereses_promocionales(self) -> pd.DataFrame:
        """
        Procesa los datos de promociones y calcula el interés promocional para cada registro.

        Returns:
            pd.DataFrame: DataFrame con columnas:
                [ID, SECUENCIA_CORTE, MONTO_ORIGINAL, MONTO_TOTAL, MONTO_PENDIENTE,
                 TASA_INTERES, TIPO_PROMO, Fecha_Corte, Min_Fecha_Transaccion,
                 Dias_Promocion, Interes_Promocional].
        """
        df = self._merge_tablas_promos()
        df['Dias_Promocion'] = (df['FECHA_CORTE'] - df['Min_Fecha_Transaccion']).dt.days
        df['Interes_Promocional'] = df.apply(self._calcular_interes_promocional, axis=1)
        df.rename(columns={'FECHA_CORTE': 'Fecha_Corte', 'Min_Fecha_Transaccion': 'Min_Fecha_Transaccion'}, inplace=True)
        columnas_finales = [
            'ID', 'SECUENCIA_CORTE', 'MONTO_ORIGINAL', 'MONTO_TOTAL', 'MONTO_PENDIENTE',
            'TASA_INTERES', 'TIPO_PROMO', 'Fecha_Corte', 'Min_Fecha_Transaccion',
            'Dias_Promocion', 'Interes_Promocional'
        ]
        return df[columnas_finales].copy()

    # -------------------------------------------------------------------------
    # CÁLCULO DE SALDO AL CIERRE DE MES
    # -------------------------------------------------------------------------
    def calcular_saldo_cierre_calculado(self) -> pd.DataFrame:
        """
        Calcula el Saldo al Cierre de Mes replicando la fórmula DAX, sumando compras, intereses y comisiones,
        restando los pagos, y calculando las diferencias con el saldo reportado.

        Returns:
            pd.DataFrame: DataFrame con columnas:
                [ID, FECHA_CORTE, SALDO_INICIAL, PAGOS_TOTALES, SALDO_CIERRE,
                 Saldo_Cierre_Calculado, Diferencia_Saldo, Diferencia_Saldo_Absoluta,
                 Diferencia_Saldo_Porcentual].
        """
        cuentas_df = self.cuentas_octubre.copy()
        cuentas_df['InicioMes'] = cuentas_df['FECHA_CORTE'].apply(
            lambda x: x.replace(day=1) if pd.notna(x) else pd.NaT
        )
        mov_join = pd.merge(self.movimientos_octubre, cuentas_df[['ID', 'FECHA_CORTE', 'InicioMes']], on='ID', how='left')
        mov_join['Hora_Transaccion'] = mov_join['FECHA_TRANSACCION'].dt.hour
        filtro = (
            (mov_join['FECHA_TRANSACCION'] >= mov_join['InicioMes']) &
            (mov_join['FECHA_TRANSACCION'] <= mov_join['FECHA_CORTE']) &
            (mov_join['Hora_Transaccion'] < 22)
        )
        mov_filtrado = mov_join[filtro].copy()
        grp = mov_filtrado.groupby(['ID', 'CODIGO'], as_index=False)['MONTO_FACTURACION'].sum()
        pivot = grp.pivot(index='ID', columns='CODIGO', values='MONTO_FACTURACION').fillna(0)
        pivot.reset_index(inplace=True)
        pivot.rename(columns={'COMPRA': 'Compras', 'INTERES': 'Intereses', 'COMISION': 'Comisiones'}, inplace=True)
        for col in ['Compras', 'Intereses', 'Comisiones']:
            if col not in pivot.columns:
                pivot[col] = 0.0
        cierre_df = pd.merge(cuentas_df, pivot[['ID', 'Compras', 'Intereses', 'Comisiones']], on='ID', how='left').fillna(0)
        cierre_df['Saldo_Cierre_Calculado'] = (
            cierre_df['SALDO_INICIAL'] + cierre_df['Compras'] + cierre_df['Intereses'] + cierre_df['Comisiones'] -
            cierre_df['PAGOS_TOTALES']
        )
        cierre_df['Diferencia_Saldo'] = cierre_df['Saldo_Cierre_Calculado'] - cierre_df['SALDO_CIERRE']
        cierre_df['Diferencia_Saldo_Absoluta'] = cierre_df['Diferencia_Saldo'].abs()
        cierre_df['Diferencia_Saldo_Porcentual'] = (cierre_df['Diferencia_Saldo'] / cierre_df['SALDO_CIERRE']).fillna(0)
        columnas_finales = [
            'ID', 'FECHA_CORTE', 'SALDO_INICIAL', 'PAGOS_TOTALES', 'SALDO_CIERRE',
            'Saldo_Cierre_Calculado', 'Diferencia_Saldo', 'Diferencia_Saldo_Absoluta', 'Diferencia_Saldo_Porcentual'
        ]
        return cierre_df[columnas_finales].copy()

    # -------------------------------------------------------------------------
    # CÁLCULO DE PAGO PARA NO GENERAR INTERESES
    # -------------------------------------------------------------------------
    def _pago_no_genera_intereses_row(self, row) -> float:
        """
        Calcula el Pago para No Generar Intereses para una fila utilizando la fórmula:
            Pago = Saldo_Cierre - (SaldoPromo + InteresPromo) + ParcialidadPromo + MontoVencido.
        
        Args:
            row (pd.Series): Fila con columnas: Saldo_Cierre, MONTO_PENDIENTE, INTERES_TOTAL, PARCIALIDAD, Monto_Vencido.
        
        Returns:
            float: Pago calculado.
        """
        saldo_cierre = row.get('Saldo_Cierre', 0)
        saldo_promo = row.get('MONTO_PENDIENTE', 0)
        interes_promo = row.get('INTERES_TOTAL', 0)
        parcialidad = row.get('PARCIALIDAD', 0)
        monto_vencido = row.get('Monto_Vencido', 0)
        sobregiro = 0  # Se asume 0 o se puede ajustar según datos reales
        iva = 0
        return saldo_cierre - (saldo_promo + interes_promo) + parcialidad + monto_vencido + sobregiro + iva

    def _saldo_cierre_calculado_row(self, row) -> float:
        """
        Retorna el valor de Saldo_Cierre (emulando un lookup en CUENTAS_OCTUBRE).
        
        Args:
            row (pd.Series): Fila del DataFrame.
        
        Returns:
            float: Valor del Saldo_Cierre.
        """
        return row.get('Saldo_Cierre', 0)

    def calcular_pago_no_generar_intereses(self) -> pd.DataFrame:
        """
        Calcula el Pago para No Generar Intereses para cuentas de octubre y sus diferencias.

        Returns:
            pd.DataFrame: DataFrame con columnas:
              [ID, SECUENCIA_CORTE, MONTO_ORIGINAL, MONTO_TOTAL, MONTO_PENDIENTE, INTERES_TOTAL,
               PARCIALIDAD, TASA_INTERES, TIPO_PROMO, Saldo_Cierre, Monto_Vencido,
               Pago_No_Genera_Intereses, Saldo_Cierre_Calculado, Diferencia_Saldo,
               Diferencia_Saldo_Absoluta, Diferencia_Saldo_Porcentual].
        """
        promos_cols = [
            'ID', 'SECUENCIA_CORTE', 'MONTO_ORIGINAL', 'MONTO_TOTAL', 'MONTO_PENDIENTE',
            'INTERES_TOTAL', 'PARCIALIDAD', 'TASA_INTERES', 'TIPO_PROMO'
        ]
        promos_summary = self.promos_octubre[promos_cols].drop_duplicates()
        cuentas_cols = ['ID', 'SALDO_CIERRE', 'MONTO_VENCIDO']
        merged_df = pd.merge(promos_summary, self.cuentas_octubre[cuentas_cols], how='left', on='ID')
        merged_df.rename(columns={'SALDO_CIERRE': 'Saldo_Cierre', 'MONTO_VENCIDO': 'Monto_Vencido'}, inplace=True)
        merged_df['Pago_No_Genera_Intereses'] = merged_df.apply(self._pago_no_genera_intereses_row, axis=1)
        merged_df['Saldo_Cierre_Calculado'] = merged_df.apply(self._saldo_cierre_calculado_row, axis=1)
        merged_df['Diferencia_Saldo'] = merged_df['Saldo_Cierre_Calculado'] - merged_df['Saldo_Cierre']
        merged_df['Diferencia_Saldo_Absoluta'] = merged_df['Diferencia_Saldo'].abs()
        merged_df['Diferencia_Saldo_Porcentual'] = (merged_df['Diferencia_Saldo'] / merged_df['Saldo_Cierre']).fillna(0)
        final_cols = [
            'ID', 'SECUENCIA_CORTE', 'MONTO_ORIGINAL', 'MONTO_TOTAL', 'MONTO_PENDIENTE',
            'INTERES_TOTAL', 'PARCIALIDAD', 'TASA_INTERES', 'TIPO_PROMO',
            'Saldo_Cierre', 'Monto_Vencido', 'Pago_No_Genera_Intereses',
            'Saldo_Cierre_Calculado', 'Diferencia_Saldo', 'Diferencia_Saldo_Absoluta', 'Diferencia_Saldo_Porcentual'
        ]
        return merged_df[final_cols].copy()

    # -------------------------------------------------------------------------
    # CÁLCULO DE PAGO MÍNIMO
    # -------------------------------------------------------------------------
    def _pago_minimo_calculado_row(self, row) -> float:
        """
        Calcula el Pago Mínimo evaluando tres escenarios:
          - Pago1: LimiteCredito * 1.25%
          - Pago2: ((Saldo_Final - SaldoPromo) * 5%) + (ParcialidadPromo * 5%)
          - Pago3: (((Saldo_Final - SaldoPromo) * 1.5%) + (InteresCargo + IVA_ISR)) * 0.015 + (InteresCargo + IVA_ISR)
        
        Retorna el valor (conservando el signo) del escenario con mayor valor absoluto.
        """
        limite_credito = row.get('Limite_Credito', 0)
        saldo_final = row.get('Saldo_Final', 0)
        saldo_promo = row.get('MONTO_PENDIENTE', 0)
        interes_cargo = row.get('INTERES_TOTAL', 0)
        parcialidad_promo = row.get('PARCIALIDAD', 0)
        sobregiro = 0
        iva_isr = 0
        
        pago1 = limite_credito * 0.0125
        pago2 = ((saldo_final - saldo_promo) * 0.05) + (parcialidad_promo * 0.05)
        base_pago3 = ((saldo_final - saldo_promo) * 0.015) + (interes_cargo + iva_isr)
        pago3 = (base_pago3 * 0.015) + (interes_cargo + iva_isr)
        
        abs_p1, abs_p2, abs_p3 = abs(pago1), abs(pago2), abs(pago3)
        if abs_p1 >= abs_p2 and abs_p1 >= abs_p3:
            return pago1
        elif abs_p2 >= abs_p3:
            return pago2
        else:
            return pago3

    def calcular_pago_minimo(self) -> pd.DataFrame:
        """
        Calcula el Pago Mínimo para cuentas de octubre evaluando tres escenarios y seleccionando
        el de mayor valor absoluto.

        Returns:
            pd.DataFrame: DataFrame con columnas:
                [ID, SECUENCIA_CORTE, MONTO_ORIGINAL, MONTO_TOTAL, MONTO_PENDIENTE, INTERES_TOTAL,
                 PARCIALIDAD, TASA_INTERES, TIPO_PROMO, Limite_Credito, Saldo_Final, Pago_Minimo_Registrado,
                 Pago1, Pago2, Pago3, Pago_Minimo_Calculado,
                 Diferencia_Pago_Minimo, Diferencia_Pago_Minimo_Absoluta, Diferencia_Pago_Minimo_Porcentual].
        """
        promos_cols = [
            'ID', 'SECUENCIA_CORTE', 'MONTO_ORIGINAL', 'MONTO_TOTAL', 'MONTO_PENDIENTE',
            'INTERES_TOTAL', 'PARCIALIDAD', 'TASA_INTERES', 'TIPO_PROMO'
        ]
        promos_summary = self.promos_octubre[promos_cols].drop_duplicates()
        cuentas_cols = ['ID', 'LIMITE_CREDITO', 'SALDO_CIERRE', 'PAGO_MINIMO']
        merged_df = pd.merge(promos_summary, self.cuentas_octubre[cuentas_cols], how='left', on='ID')
        merged_df.rename(columns={
            'LIMITE_CREDITO': 'Limite_Credito',
            'SALDO_CIERRE': 'Saldo_Final',
            'PAGO_MINIMO': 'Pago_Minimo_Registrado'
        }, inplace=True)
        merged_df['Pago1'] = merged_df['Limite_Credito'] * 0.0125
        merged_df['Pago2'] = (merged_df['Saldo_Final'] - merged_df['MONTO_PENDIENTE']) * 0.05
        merged_df['Pago3'] = (((merged_df['Saldo_Final'] - merged_df['MONTO_PENDIENTE']) * 0.015) + merged_df['INTERES_TOTAL']) * 0.015 + merged_df['INTERES_TOTAL']
        merged_df['Pago_Minimo_Calculado'] = merged_df.apply(self._pago_minimo_calculado_row, axis=1)
        merged_df['Diferencia_Pago_Minimo'] = merged_df['Pago_Minimo_Calculado'] - merged_df['Pago_Minimo_Registrado']
        merged_df['Diferencia_Pago_Minimo_Absoluta'] = merged_df['Diferencia_Pago_Minimo'].abs()
        merged_df['Diferencia_Pago_Minimo_Porcentual'] = (merged_df['Diferencia_Pago_Minimo'] / merged_df['Pago_Minimo_Registrado']).fillna(0)
        final_cols = [
            'ID', 'SECUENCIA_CORTE', 'MONTO_ORIGINAL', 'MONTO_TOTAL', 'MONTO_PENDIENTE',
            'INTERES_TOTAL', 'PARCIALIDAD', 'TASA_INTERES', 'TIPO_PROMO',
            'Limite_Credito', 'Saldo_Final', 'Pago_Minimo_Registrado',
            'Pago1', 'Pago2', 'Pago3', 'Pago_Minimo_Calculado',
            'Diferencia_Pago_Minimo', 'Diferencia_Pago_Minimo_Absoluta', 'Diferencia_Pago_Minimo_Porcentual'
        ]
        return merged_df[final_cols].copy()
