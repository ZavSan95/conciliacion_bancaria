# conciliador.py

import pandas as pd
from datetime import datetime, timedelta
import os

def cargar_datos(path_banco, path_ventas):
    """
    Carga los archivos CSV y maneja errores de lectura.
    """
    try:
        df_banco = pd.read_csv(
            path_banco,
            dtype={'idcuenta': str, 'depositos': str},
            parse_dates=['fecha'],
            dayfirst=False
        )
        df_ventas = pd.read_csv(
            path_ventas,
            dtype={'idcuenta': str},
            parse_dates=['fecha'],
            dayfirst=False
        )
        return df_banco, df_ventas
    except Exception as e:
        print(f"❌ Error al cargar los archivos CSV: {e}")
        exit(1)

def limpiar_datos(df, nombre_df):
    """
    Limpia datos: elimina duplicados y registros nulos.
    Redondea los importes para manejar centavos.
    """
    df = df.dropna(subset=['idcuenta', 'importe', 'fecha'])
    df = df.drop_duplicates()
    df['importe'] = pd.to_numeric(df['importe'], errors='coerce').round(2)
    df = df.dropna(subset=['importe'])  # Elimina importes no numéricos
    return df

def conciliar(df_banco, df_ventas, tolerancia_horas=24):
    df_banco_ = df_banco.copy()
    df_ventas_ = df_ventas.copy()

    # Conciliados exactos (fecha exacta)
    conciliados = pd.merge(
        df_banco_,
        df_ventas_,
        on=['idcuenta', 'importe', 'fecha'],
        how='inner',
        suffixes=('_banco', '_venta')
    )

    # Conciliados con tolerancia de fechas (±1 día)
    df_banco_['key'] = df_banco_['idcuenta'] + df_banco_['importe'].astype(str)
    df_ventas_['key'] = df_ventas_['idcuenta'] + df_ventas_['importe'].astype(str)

    conciliados_tol = pd.merge_asof(
        df_banco_.sort_values('fecha'),
        df_ventas_.sort_values('fecha'),
        on='fecha',
        by='key',
        direction='nearest',
        tolerance=pd.Timedelta(hours=tolerancia_horas),
        suffixes=('_banco', '_venta')
    )

    # Ventas sin depositar
    conciliados_keys = set(conciliados_tol['key'].dropna())
    ventas_sin_depositar = df_ventas_[~df_ventas_['key'].isin(conciliados_keys)].drop(columns=['key'])

    # Depósitos sin registro
    depositos_sin_registro = df_banco_[~df_banco_['key'].isin(conciliados_keys)].drop(columns=['key'])

    # Diferencias de importe
    dif_importe = pd.merge_asof(
        df_banco_.sort_values('fecha'),
        df_ventas_.sort_values('fecha'),
        on='fecha',
        by='idcuenta',
        direction='nearest',
        tolerance=pd.Timedelta(hours=tolerancia_horas),
        suffixes=('_banco', '_venta')
    )
    dif_importe = dif_importe[dif_importe['importe_banco'] != dif_importe['importe_venta']]
    dif_importe = dif_importe.dropna(subset=['importe_venta'])

    return conciliados_tol.drop(columns=['key']), ventas_sin_depositar, depositos_sin_registro, dif_importe


def generar_reporte(df_banco, df_ventas, conciliados, ventas_sin_depositar, depositos_sin_registro, dif_importe):
    """
    Genera el reporte final en consola y exporta archivos CSV de resultados.
    """
    total_banco = len(df_banco)
    total_ventas = len(df_ventas)
    total_conciliados = len(conciliados)
    porcentaje_conciliacion = (total_conciliados / total_ventas) * 100 if total_ventas else 0
    suma_diferencias = (dif_importe['importe_banco'].sum() - dif_importe['importe_venta'].sum()).round(2)

    print("\n=== REPORTE DE CONCILIACIÓN BANCARIA ===")
    print("Fecha:", datetime.now().date())
    print(f"Registros bancarios: {total_banco}")
    print(f"Registros de ventas: {total_ventas}\n")
    print("RESULTADOS:")
    print(f"✅ Conciliados (±24h): {total_conciliados} ({porcentaje_conciliacion:.1f}%)")
    print(f"⚠️  Ventas sin depositar: {len(ventas_sin_depositar)}")
    print(f"❌ Depósitos sin registrar: {len(depositos_sin_registro)}")
    print(f"💰 Diferencias de importe: {len(dif_importe)} (diferencia total: {suma_diferencias})\n")

    print("RESUMEN POR CUENTA:")
    for cuenta in df_ventas['idcuenta'].unique():
        ventas_cuenta = df_ventas[df_ventas['idcuenta'] == cuenta]
        conciliados_cuenta = conciliados[conciliados['idcuenta_banco'] == cuenta]
        porcentaje = (len(conciliados_cuenta) / len(ventas_cuenta)) * 100 if len(ventas_cuenta) else 0
        print(f"{cuenta}: {porcentaje:.1f}% conciliado")

    # Crear carpeta de resultados si no existe
    os.makedirs("resultados", exist_ok=True)

    # Exportar CSVs
    conciliados.to_csv("resultados/conciliados.csv", index=False)
    ventas_sin_depositar.to_csv("resultados/ventas_sin_depositar.csv", index=False)
    depositos_sin_registro.to_csv("resultados/depositos_sin_registro.csv", index=False)
    dif_importe.to_csv("resultados/diferencias_importe.csv", index=False)

def main():
    """
    Programa principal.
    """
    path_banco = "datos/extracto_bancario.csv"
    path_ventas = "datos/ventas_sistema.csv"

    # 1️⃣ Cargar datos
    df_banco, df_ventas = cargar_datos(path_banco, path_ventas)

    # 2️⃣ Limpiar datos
    df_banco = limpiar_datos(df_banco, "Banco")
    df_ventas = limpiar_datos(df_ventas, "Ventas")

    # 3️⃣ Conciliación
    conciliados, ventas_sin_depositar, depositos_sin_registro, dif_importe = conciliar(df_banco, df_ventas)

    # 4️⃣ Reporte final
    generar_reporte(df_banco, df_ventas, conciliados, ventas_sin_depositar, depositos_sin_registro, dif_importe)

if __name__ == "__main__":
    main()
