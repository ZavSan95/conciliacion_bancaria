# 📊 Conciliación Bancaria

Este proyecto es un sistema de **conciliación bancaria** en Python que compara los depósitos bancarios con las ventas registradas en el sistema interno de la empresa. Está optimizado para grandes volúmenes de datos, manejo de múltiples cuentas y tolerancia en fechas de hasta 24 horas.

---

## 🚀 Funcionalidades

✅ Carga y limpieza de archivos CSV  
✅ Comparación de registros considerando:
- Cuenta bancaria
- Importe (con precisión decimal)
- Fecha (con tolerancia ± 24 horas)  
✅ Detección de:
- Movimientos conciliados
- Ventas sin depositar
- Depósitos sin registrar
- Diferencias en importes  
✅ Reportes en consola con estadísticas claras  
✅ Generación de archivos CSV de salida en la carpeta `resultados/`

---

## 📁 Estructura del proyecto

conciliacion_bancaria/
├── datos/
│ ├── extracto_bancario.csv
│ └── ventas_sistema.csv
├── resultados/
│ ├── conciliados.csv
│ ├── ventas_sin_depositar.csv
│ ├── depositos_sin_registro.csv
│ └── diferencias_importe.csv
├── conciliador.py
└── README.md

---

## 📝 Uso

1️⃣ Clona o descarga este repositorio.

2️⃣ Coloca tus archivos `extracto_bancario.csv` y `ventas_sistema.csv` en la carpeta `datos/`.  

3️⃣ Instala las dependencias (pandas):

```bash
pip install pandas