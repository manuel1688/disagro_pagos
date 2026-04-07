# Migración a 3 Decimales - DISAGRO Inventario

## Descripción
Este documento describe el proceso de migración del sistema de inventario de 2 a 3 decimales de precisión.

## Fecha
24 de noviembre de 2025

## Archivos Modificados

### 1. Base de Datos
- **Script SQL**: `2025-11-24_migrate_to_three_decimals.sql`
- **Tablas afectadas**:
  - `TOMA_FISICA.CAPTACION_FISICA` - columna `CANTIDAD`
  - `TOMA_FISICA.EXISTENCIA_UBICACION` - columnas `CANTIDAD` y `COSTO`

### 2. Modelo ORM (Python)
- `disagro_i/clases/modelo.py`
  - Cambio de `Float` a `Numeric(15, 3)` para columnas de cantidad y costo

### 3. JavaScript
- `static/js/common.js` - Nueva función `numero_tres_decimales`
- `static/js/operaciones.js` - Actualizado para usar 3 decimales
- `static/js/operaciones_grid_venta.js` - Actualizado para usar 3 decimales

### 4. Python Backend
- `disagro_i/__init__.py` - Filtros Jinja actualizados (redondear, formatoMonto, dos_decimales)
- `disagro_i/reporte_bp.py` - Todos los `round()` cambiados de 2 a 3 decimales
- Formatos Excel actualizados: `#,##0.000`

### 5. Schema
- `base_de_datos/schema.sql` - Actualizado para reflejar `NUMERIC(15,3)`

## Pasos para Aplicar en Producción

### IMPORTANTE: Realizar Backup
```bash
# Backup de la base de datos
pg_dump -h [HOST] -U disagro -d disagro_db > backup_antes_de_3_decimales_$(date +%Y%m%d_%H%M%S).sql
```

### 1. Aplicar Script SQL
```bash
# Conectarse a la base de datos
psql -h [HOST] -U disagro -d disagro_db

# Ejecutar el script
\i sql/2025-11-24_migrate_to_three_decimals.sql

# Verificar los cambios
SELECT column_name, data_type, numeric_precision, numeric_scale 
FROM information_schema.columns 
WHERE table_schema = 'TOMA_FISICA' 
AND table_name IN ('CAPTACION_FISICA', 'EXISTENCIA_UBICACION')
AND column_name IN ('CANTIDAD', 'COSTO');

# Resultado esperado:
# column_name | data_type | numeric_precision | numeric_scale
# ------------+-----------+-------------------+--------------
# CANTIDAD    | numeric   | 15                | 3
# COSTO       | numeric   | 15                | 3
```

### 2. Verificar Datos
```sql
-- Verificar que los datos se preservaron correctamente
-- Ejemplo: un valor de 3.53 debe aparecer como 3.530

SELECT ARTICULO, CANTIDAD, COSTO 
FROM "TOMA_FISICA"."EXISTENCIA_UBICACION" 
LIMIT 10;

SELECT ARTICULO, CANTIDAD 
FROM "TOMA_FISICA"."CAPTACION_FISICA" 
LIMIT 10;
```

### 3. Desplegar Código Actualizado
```bash
# En el servidor de aplicación
cd /ruta/al/proyecto
git pull origin main  # o el branch correspondiente
# Reiniciar la aplicación Flask
```

### 4. Verificar Funcionamiento

#### Verificaciones en la Aplicación:
1. **Reportes de Diferencias**: Verificar que las cantidades se muestren con 3 decimales
2. **Captación Física**: Probar capturar una cantidad con 3 decimales (ej: 125.375)
3. **Reconteo**: Verificar cálculos de diferencias con 3 decimales
4. **Exportación Excel**: Verificar que los archivos XLS muestren formato `#,##0.000`
5. **Reportes Consolidados**: Verificar totales y sumas

#### Casos de Prueba:
```
Caso 1: Cantidad con 3 decimales
- Capturar: 10.125
- Sistema: 10.000
- Diferencia esperada: 0.125

Caso 2: Preservación de datos existentes
- Valor antiguo: 3.53
- Valor después de migración: 3.530
- Diferencia: 0.000 (sin cambio real)

Caso 3: Cálculos de costo
- Cantidad: 5.375
- Costo unitario: 12.500
- Total esperado: 67.188
```

## Reversión (Si es Necesario)

En caso de problemas, se puede revertir:

```sql
BEGIN;

ALTER TABLE "TOMA_FISICA"."CAPTACION_FISICA"
    ALTER COLUMN "CANTIDAD" TYPE NUMERIC(15,2);

ALTER TABLE "TOMA_FISICA"."EXISTENCIA_UBICACION"
    ALTER COLUMN "CANTIDAD" TYPE NUMERIC(15,2),
    ALTER COLUMN "COSTO" TYPE NUMERIC(15,2);

COMMIT;
```

**NOTA**: Al revertir a 2 decimales, los valores se redondearán automáticamente:
- 10.125 → 10.13
- 10.124 → 10.12

## Compatibilidad

- **PostgreSQL**: 9.6+
- **Python**: 3.11+
- **SQLAlchemy**: Compatible con `Numeric(precision, scale)`
- **Navegadores**: Todos los navegadores modernos soportan JavaScript

## Notas Técnicas

1. **No hay pérdida de datos**: La migración de `DECIMAL` a `NUMERIC(15,3)` preserva todos los datos existentes, solo añade un decimal adicional.

2. **Compatibilidad con código antiguo**: Se mantuvo `numero_dos_decimales` como alias de `numero_tres_decimales` para compatibilidad.

3. **Performance**: No hay impacto significativo en performance. Los cálculos con 3 decimales son igual de rápidos.

4. **Validaciones**: Las validaciones de input deben actualizarse para aceptar 3 decimales en lugar de 2.

## Contacto
Para dudas o problemas con la migración, contactar al equipo de desarrollo.
