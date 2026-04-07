-- Script de migración: Cambiar sistema de 2 a 3 decimales
-- Fecha: 2025-11-24
-- Descripción: Actualiza las columnas CANTIDAD y COSTO para soportar 3 decimales
-- Los datos existentes se preservan automáticamente (ej: 3.53 → 3.530)

-- IMPORTANTE: Realizar backup de la base de datos antes de ejecutar este script

BEGIN;

-- Actualizar columna CANTIDAD en CAPTACION_FISICA
ALTER TABLE "TOMA_FISICA"."CAPTACION_FISICA"
    ALTER COLUMN "CANTIDAD" TYPE NUMERIC(15,3);

-- Actualizar columnas CANTIDAD y COSTO en EXISTENCIA_UBICACION
ALTER TABLE "TOMA_FISICA"."EXISTENCIA_UBICACION"
    ALTER COLUMN "CANTIDAD" TYPE NUMERIC(15,3),
    ALTER COLUMN "COSTO" TYPE NUMERIC(15,3);

-- Agregar comentarios para documentación
COMMENT ON COLUMN "TOMA_FISICA"."CAPTACION_FISICA"."CANTIDAD" IS 'Cantidad física capturada con 3 decimales de precisión';
COMMENT ON COLUMN "TOMA_FISICA"."EXISTENCIA_UBICACION"."CANTIDAD" IS 'Cantidad en existencia con 3 decimales de precisión';
COMMENT ON COLUMN "TOMA_FISICA"."EXISTENCIA_UBICACION"."COSTO" IS 'Costo unitario con 3 decimales de precisión';

COMMIT;

-- Verificación post-migración (ejecutar después del COMMIT)
-- SELECT column_name, data_type, numeric_precision, numeric_scale 
-- FROM information_schema.columns 
-- WHERE table_schema = 'TOMA_FISICA' 
-- AND table_name IN ('CAPTACION_FISICA', 'EXISTENCIA_UBICACION')
-- AND column_name IN ('CANTIDAD', 'COSTO');
