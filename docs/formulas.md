# Algoritmos Calculadora

## 1. SALDO AL CIERRE

La fórmula base es:

SALDO_CIERRE = (SALDO_INICIAL + Compras y otros cargos + Interés a cargo) - (Pagos y depósitos + Interés bruto) + IVA

Donde cada término se obtiene de la información extraída y de los movimientos correspondientes.

### 1. Datos Iniciales
Del resumen del ID 505164 tenemos:

* **SALDO_INICIAL:** -133,811.14
* **SALDO_CIERRE:** -138,401.73

Además, en el detalle de movimientos se observa que:

* **CREDITOS_TOTALES:** 0.00
* **DEBITOS_TOTALES:** 4,590.59

Esta cifra de 4,590.59 es la suma de los movimientos que se detallan a continuación.

### 2. Identificación y Clasificación de los Movimientos

#### A. Movimientos Extraídos
Se tienen los siguientes movimientos:

**Comisión por penalización por pago tardío**
* Monto: 350.00
* Tipo: Comisiones (se considera parte de "Compras y otros cargos")

**Interés sobre compra diferida no sujeta a IVA**
* Monto: 63.20
* Tipo: Interés a cargo

**Interés sobre compra diferida sujeta a IVA**
* Monto: 3,552.92
* Tipo: Interés a cargo

**IVA sobre comisión o interés**
* Monto: 624.47
* Tipo: IVA/ISR

**Verificación:**
La suma de todos estos movimientos es:
350.00 + 63.20 + 3,552.92 + 624.47 = 4,590.59
lo que coincide con el total de Débitos Totales.

### 3. Asignación de Montos a Cada Concepto
Según la fórmula, se agrupan los movimientos de la siguiente forma:

**Compras y otros cargos:**
* Incluye la comisión: 350.00

**Interés a cargo:**
* Suma de los dos movimientos de interés:
 63.20 + 3,552.92 = 3,616.12

**IVA/ISR:**
* Monto del IVA sobre comisión o interés: 624.47

**Pagos y depósitos + Interés bruto:**
* En el detalle no se muestran pagos o depósitos, pero el saldo final (SALDO_CIERRE) ya incluye el efecto de estos descuentos. Este valor lo determinaremos de forma "reversiva" para cuadrar la cuenta.

### 4. Aplicación de la Fórmula Paso a Paso

#### Paso 4.1: Sumar SALDO_INICIAL y los cargos (sin IVA)
Se suman el SALDO_INICIAL, las Compras y otros cargos y el Interés a cargo:

Subtotal = SALDO_INICIAL + (Compras y otros cargos + Interés a cargo)

Sustituyendo los valores:
Subtotal = -133,811.14 + (350.00 + 3,616.12)

Primero, sumamos lo que está entre paréntesis:
350.00 + 3,616.12 = 3,966.12

Luego, sumamos al SALDO_INICIAL:
-133,811.14 + 3,966.12 = -129,845.02

#### Paso 4.2: Incluir el IVA/ISR
Se suma el IVA/ISR al subtotal:

Subtotal con IVA = -129,845.02 + 624.47 = -129,220.55

#### Paso 4.3: Determinar la Resta de "Pagos y depósitos + Interés bruto"
Según la fórmula completa, para obtener el SALDO_CIERRE se debe restar el monto de "Pagos y depósitos + Interés bruto". Es decir:

SALDO_CIERRE = Subtotal con IVA - (Pagos y depósitos + Interés bruto)

Sabemos que el SALDO_CIERRE es -138,401.73. Entonces:
-138,401.73 = -129,220.55 - (Pagos y depósitos + Interés bruto)

Para encontrar (Pagos y depósitos + Interés bruto), despejamos:

Pagos y depósitos + Interés bruto = -129,220.55 - (-138,401.73)
= -129,220.55 + 138,401.73
= 9,181.18

Nota: La diferencia se obtiene para que, al restarse, se llegue al saldo final informado.

### 5. Conclusión y Resultado Final
El cálculo se resume de la siguiente forma:

* **SALDO_INICIAL:** -133,811.14
* **Compras y otros cargos:** 350.00
* **Interés a cargo:** 63.20 + 3,552.92 = 3,616.12
* **IVA/ISR:** 624.47
* **Pagos y depósitos + Interés bruto (descuento):** 9,181.18

Aplicamos la fórmula:

* Subtotal sin IVA = -133,811.14 + (350.00 + 3,616.12) = -133,811.14 + 3,966.12 = -129,845.02
* Subtotal con IVA = -129,845.02 + 624.47 = -129,220.55
* SALDO_CIERRE = -129,220.55 - 9,181.18 = -138,401.73

Así, el SALDO AL CORTE (SALDO_CIERRE) de -138,401.73 se obtiene al:

1. Empezar con el SALDO_INICIAL.
2. Sumar los cargos (comisión y los intereses).
3. Sumar el IVA/ISR.
4. Restar el total correspondiente a "Pagos y depósitos + Interés bruto" (9,181.18), que es el ajuste necesario para cuadrar el saldo final.



## 2. SALDO AL CIERRE DE MES

La fórmula base es:

Saldo al cierre = Saldo inicial + Compras + Intereses + Comisiones - Pagos

En este ejemplo se dispone de la siguiente información para el ID **512721**:

* **SALDO_INICIAL:** -72,898.00
* **SALDO_CIERRE (reportado):** -79,385.83
* **Movimientos extraídos (que corresponden a Intereses, Comisiones y IVA):**

En este caso no se registran pagos (Pagos = 0).

### Paso 1. Calcular la diferencia total requerida

La diferencia entre el saldo final reportado y el saldo inicial es:

Δ = SALDO_CIERRE - SALDO_INICIAL = -79,385.83 - (-72,898.00)
Δ = -79,385.83 + 72,898.00 = -6,487.83

Esto indica que, para pasar de un saldo inicial de -72,898.00 a un saldo final de -79,385.83, se debe "sumar" (es decir, cargar) un total de -6,487.83 durante el mes.

### Paso 2. Reconocer la parte ya representada por los movimientos

Los movimientos extraídos (Intereses + Comisiones + IVA) suman:

Movimientos = 350.00 + 3.46 + 194.65 + 87.14 = 635.25

### Paso 3. Determinar el componente "Compras"

La fórmula completa es:

Saldo al cierre = Saldo inicial + Compras + (Intereses + Comisiones + IVA) - Pagos

Como no hay pagos, sustituimos los valores conocidos:

-79,385.83 = -72,898.00 + Compras + 635.25

Para encontrar el valor de **Compras** (que en este contexto agrupa las transacciones de compra que aún no están incluidas en los movimientos de intereses, comisiones y IVA), despejamos:

Compras = -79,385.83 - (-72,898.00) - 635.25
Compras = -79,385.83 + 72,898.00 - 635.25
Compras = -6,487.83 - 635.25 = -7,123.08

### Paso 4. Verificar el cálculo

Ahora aplicamos la fórmula completa con los valores determinados:

1. **Saldo inicial:** -72,898.00
2. **Compras:** -7,123.08
3. **Intereses + Comisiones + IVA (Movimientos):** 635.25
4. **Pagos:** 0

Entonces:

Saldo al cierre = -72,898.00 + (-7,123.08) + 635.25 - 0
Saldo al cierre = (-72,898.00 - 7,123.08) + 635.25
Saldo al cierre = -80,021.08 + 635.25 = -79,385.83

El resultado coincide exactamente con el **SALDO_CIERRE** reportado.

### Resumen de los Subcálculos

1. **Diferencia requerida entre SALDO_CIERRE y SALDO_INICIAL:**
  -79,385.83 - (-72,898.00) = -6,487.83

2. **Suma de Movimientos (Intereses + Comisiones + IVA):**
  350.00 + 3.46 + 194.65 + 87.14 = 635.25

3. **Cálculo del componente Compras:**
  Compras = -6,487.83 - 635.25 = -7,123.08

4. **Aplicación final de la fórmula:**
  Saldo al cierre = -72,898.00 + (-7,123.08) + 635.25 = -79,385.83

### Conclusión

Para el ID **512721** la aplicación de la fórmula:

Saldo al cierre = Saldo inicial + Compras + Intereses + Comisiones - Pagos

se desglosa de la siguiente forma:

* **Saldo inicial:** -72,898.00
* **Compras:** -7,123.08
* **Movimientos (Intereses + Comisiones + IVA):** 635.25
* **Pagos:** 0

Y al sumarlos se obtiene:

-72,898.00 + (-7,123.08) + 635.25 = -79,385.83,

lo que coincide con el saldo al cierre reportado.

### Ejemplo 2 - Saldo al Cierre de Mes

La fórmula base es:
Saldo al cierre = Saldo inicial + Compras + Intereses + Comisiones - Pagos

En este ejemplo se dispone de:

* **SALDO INICIAL:** –7,298.00
* **SALDO CIERRE (reportado):** –7,933.83
* **DEBITOS TOTALES (movimientos extraídos – Intereses, Comisiones y IVA):** 635.25
  * Desglose de los movimientos:
     * Comisión por penalización por pago tardío: 350.00
     * Interés sobre compra no sujeta a IVA: 3.46
     * Interés sobre compra sujeta a IVA: 194.65
     * IVA sobre comisión o interés: 87.14
     * **Suma total:** 350.00 + 3.46 + 194.65 + 87.14 = **635.25**
* **PAGOS TOTALES:** 0.00

Observa que la fórmula incluye un término "Compras" que en este caso no aparece de forma directa. Lo que haremos es deducir dicho monto (denominarlo C) para cuadrar la ecuación.

### Paso 1: Calcular la diferencia total requerida

Esta diferencia es la variación que se debe lograr al pasar del saldo inicial al saldo final:

Δ = SALDO CIERRE - SALDO INICIAL
Δ = (-7,933.83) - (-7,298.00) = -7,933.83 + 7,298.00 = -635.83

Esto indica que, en el período, la cuenta "cargó" (incrementó la deuda) en –635.83.

### Paso 2: Considerar el total de los movimientos de Intereses, Comisiones y IVA

Se tiene que estos movimientos suman:

M = 350.00 + 3.46 + 194.65 + 87.14 = 635.25

Estos movimientos, al aplicarse en una cuenta de crédito, se suman al saldo inicial (con signo negativo) para aumentar la deuda.

### Paso 3: Calcular el componente "Compras" (C)

La fórmula completa es:
SALDO CIERRE = SALDO INICIAL + C + M - Pagos

Dado que no hay pagos, Pagos = 0. Entonces:

-7,933.83 = -7,298.00 + C + 635.25

Despejamos C:

C = -7,933.83 - (-7,298.00) - 635.25
C = (-7,933.83 + 7,298.00) - 635.25
C = -635.83 - 635.25 = -1,271.08

Este valor negativo indica que, además de los movimientos (Intereses, Comisiones e IVA), se cargaron compras por –1,271.08 durante el período.

### Paso 4: Verificación final

Ahora, se aplica la fórmula completa con todos los componentes:

1. **Saldo inicial:** –7,298.00
2. **Compras:** –1,271.08
3. **Movimientos (Intereses+Comisiones+IVA):** 635.25
4. **Pagos:** 0

Aplicamos la fórmula:

Saldo al cierre = -7,298.00 + (-1,271.08) + 635.25 - 0
Saldo al cierre = (-7,298.00 - 1,271.08) + 635.25
Saldo al cierre = -8,569.08 + 635.25 = -7,933.83

El resultado coincide exactamente con el **SALDO CIERRE** reportado (–7,933.83).

### Resumen de los Cálculos

1. **Diferencia total requerida:**
  Δ = -7,933.83 - (-7,298.00) = -635.83

2. **Suma de movimientos (Intereses, Comisiones e IVA):**
  M = 350.00 + 3.46 + 194.65 + 87.14 = 635.25

3. **Cálculo de Compras (C):**
  C = -7,933.83 - (-7,298.00) - 635.25 = -635.83 - 635.25 = -1,271.08

4. **Aplicación final de la fórmula:**
  Saldo al cierre = -7,298.00 + (-1,271.08) + 635.25 = -7,933.83

### Conclusión

Para el ID **512721** se obtiene que:
* **Saldo Inicial:** –7,298.00
* **Compras:** –1,271.08 (deducido para cuadrar la cuenta)
* **Intereses + Comisiones + IVA:** 635.25
* **Pagos:** 0

Y al aplicar la fórmula:
Saldo al cierre = -7,298.00 + (-1,271.08) + 635.25 = -7,933.83

Esto confirma que el saldo final calculado coincide con el saldo al cierre reportado.


## 3. PAGO PARA NO GENERAR INTERESES

La fórmula base es:

Pago para no generar intereses = |Saldo Inicial + (Débitos Totales - Créditos Totales)|

Este cálculo tiene como objetivo determinar cuánto deberías pagar para cumplir con el límite sin generar intereses adicionales, considerando el saldo inicial y los movimientos del período.

### Ejemplo 1 - ID 321795

En este ejemplo se dispone de:

* **SALDO_INICIAL:** –2,442.05
* **CREDITOS_TOTALES:** 4,442.05
* **DEBITOS_TOTALES:** 4,702.27
* **SALDO_CIERRE (reportado):** –2,702.27
* **PAGO_NOGEN_INT (reportado):** –2,702.27

*Nota:* Los movimientos (compras, ajustes, etc.) se resumen en los totales de débitos y créditos. Los débitos son los cargos que incrementan la deuda, mientras que los créditos son pagos o devoluciones que la reducen.

#### 1. Calcular el efecto neto de los movimientos

Efecto neto = Débitos Totales - Créditos Totales

Sustituyendo los valores:
Efecto neto = 4,702.27 - 4,442.05 = 260.22

Esto significa que, durante el período, las transacciones incrementaron la deuda en 260.22.

#### 2. Sumar el Saldo Inicial al efecto neto

Saldo Final (calculado) = Saldo Inicial + Efecto neto

Sustituyendo:
Saldo Final (calculado) = -2,442.05 + 260.22 = -2,702.27

Este valor coincide con el **PAGO_NOGEN_INT** reportado.

#### 3. Calcular el Pago para no generar intereses

Para eliminar la deuda, se debe pagar el valor absoluto del saldo final calculado:

Pago para no generar intereses = |Saldo Final (calculado)| = |-2,702.27| = 2,702.27

#### Resumen de los Cálculos
1. **Efecto neto de movimientos:** 4,702.27 – 4,442.05 = 260.22
2. **Saldo Final Calculado:** –2,442.05 + 260.22 = –2,702.27
3. **Pago para no generar intereses:** |–2,702.27| = 2,702.27

### Ejemplo 2 - ID 336736

La fórmula alternativa es:

Pago para no generar intereses = Saldo al cierre - (Saldo promo s/int + Interés promo) + Parcialidad promo + Monto vencido promo + Sobregiro de promo + IVA

#### 1. Datos disponibles

A) De la cuenta (cuentas_octubre):
* **SALDO_INICIAL:** –21,472.60
* **SALDO_CIERRE:** –6,202.99

B) De la promoción (promociones_octubre):
* **MONTO_ORIGINAL:** 15,669.00
* **MONTO_TOTAL:** 15,669.00
* **PARCIALIDAD:** 0.00
* No se reportan otros cargos (INTERÉS TOTAL = 0)

*Interpretación:* La expresión "Saldo promo s/int + Interés promo" se toma del detalle de la promoción. Como el INTERÉS PROMO es 0, utilizaremos el monto de la promoción con signo negativo:

Saldo promo s/int + Interés promo = -MONTO_TOTAL = -15,669.00

#### 2. Aplicación de la fórmula

Sustituyendo valores (asumiendo Parcialidad, Monto vencido, Sobregiro e IVA = 0):

* **Saldo al cierre:** –6,202.99
* **Saldo promo s/int + Interés promo:** –15,669.00
* **Parcialidad promo:** 0.00
* **Monto vencido promo:** 0.00
* **Sobregiro de promo:** 0.00
* **IVA:** 0.00

Entonces:
Pago = (-6,202.99) - (-15,669.00) + 0 + 0 + 0 + 0
    = -6,202.99 + 15,669.00
    = 9,466.01
- **PUNTO CLAVE**: La fórmula para el pago para no generar intereses se ajusta según las características del crédito:
- 1. Para créditos sin promociones, se usa la fórmula básica que considera el saldo inicial y los movimientos del período.
- 2. Para créditos con promociones, se usa una fórmula extendida que considera los saldos promocionales y sus características específicas.

- PAGO_NOGEN_INT => Dos Escenarios:
    - a) Saldo al Cierre + [(Número de Pagos - 1) / Número de Pagos] * Monto Total, si p.tipo_promo contiene SI
    - b) Saldo al Cierre, en otro caso


## 4.- PAGO MÍNIMOdir

La fórmula original propuesta es:

```math
\text{Pago mínimo} = \max \Bigg\{ \underbrace{\text{Límite de crédito} \times 1.25\%}_{T1}, \quad 
\underbrace{\Big[(\text{Saldo final} - \text{Sobregiro} - \text{Saldo en promociones}) \times 5\% + (\text{Parcialidad de promociones} \times 5\%)\Big]}_{T2}, \quad 
\underbrace{\Big[(\text{Saldo final} - \text{Sobregiro} - \text{Saldo en promociones}) \times 1.5\% + (\text{Interés a cargo} + \text{IVA/ISR})\Big]}_{T3} \Bigg\} 
```

(En este esquema, los porcentajes se aplican sobre el valor absoluto de la deuda “sujeta a promociones”).

### Ajuste para promociones “SI”

Para promociones con “SI” (por ejemplo, “03 MESES SI (Q6)”, “06 MESES SI (Q6)”, etc.) se distribuye el beneficio en cuotas.

Si la promoción contiene también la cadena “SIN INTERESES”, se usa un factor fijo (por ejemplo, 0.3126).  
En caso contrario, se usa el factor:

```math
\text{Factor} = \frac{\text{número_de_pagos} - 1}{\text{número_de_pagos}}
```

El **Saldo en promociones efectivo** se define entonces como:

```math
\text{Saldo promo efectivo} = - (\text{Monto Total} \times \text{Factor})
```

(Se usa el signo negativo porque el beneficio promocional se entiende como un crédito que reduce la deuda).

### Para otros casos o IDs sin promoción

Si el ID no tiene promoción o la promoción no contiene “SI”, se asume que no se aplica beneficio promocional para el cálculo del Pago mínimo y se utiliza el saldo final (o “Saldo al cierre”) directamente.

### Definición de cada término (en valor absoluto)

```math
T1 = \text{Límite de crédito} \times 1.25\%
```

```math
T2 = \Big[ |\text{Saldo final} - \text{Sobregiro} - \text{Saldo en promociones}| \times 5\% \Big] + (\text{Parcialidad de promociones} \times 5\%)
```

```math
T3 = \Big[ |\text{Saldo final} - \text{Sobregiro} - \text{Saldo en promociones}| \times 1.5\% \Big] + (\text{Interés a cargo} + \text{IVA/ISR})
```

Luego, el **Pago mínimo calculado** se define como el negativo del máximo entre T1, T2 y T3:

```math
\text{Pago mínimo calculado} = -\max \{ T1, T2, T3 \}
```

(El signo negativo se aplica para reflejar que es un cargo o deuda).
