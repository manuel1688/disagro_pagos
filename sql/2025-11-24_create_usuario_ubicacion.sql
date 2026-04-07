-- ================================================================
-- Script: Crear tabla USUARIO_UBICACION
-- Fecha: 2025-11-24
-- Descripción: Crea la tabla USUARIO_UBICACION para asignar ubicaciones a usuarios
-- NOTA: ESTE SCRIPT ESTÁ COMENTADO - La funcionalidad de ubicaciones por usuario
--       ya no se utiliza. El sistema ahora asigna ubicaciones a través de 
--       PLANIFICACION_LINEA, no directamente a usuarios.
-- ================================================================

-- BEGIN;

-- -- Crear tabla USUARIO_UBICACION si no existe
-- CREATE TABLE IF NOT EXISTS "TOMA_FISICA"."USUARIO_UBICACION" (
--     "ID_USUARIO_UBICACION" SERIAL PRIMARY KEY,
--     "USUARIO" VARCHAR(255) NOT NULL,
--     "ID_UBICACION" VARCHAR(50) NOT NULL,
--     FOREIGN KEY ("USUARIO") REFERENCES "TOMA_FISICA"."usuario" ("usuario") ON DELETE CASCADE,
--     FOREIGN KEY ("ID_UBICACION") REFERENCES "TOMA_FISICA"."UBICACION" ("UBICACION") ON DELETE CASCADE,
--     UNIQUE("USUARIO", "ID_UBICACION")
-- );

-- -- Crear índices para mejorar el rendimiento
-- CREATE INDEX IF NOT EXISTS "idx_usuario_ubicacion_usuario" 
--     ON "TOMA_FISICA"."USUARIO_UBICACION" ("USUARIO");

-- CREATE INDEX IF NOT EXISTS "idx_usuario_ubicacion_ubicacion" 
--     ON "TOMA_FISICA"."USUARIO_UBICACION" ("ID_UBICACION");

-- COMMIT;

-- ================================================================
-- VERIFICACIÓN
-- ================================================================
-- Para verificar que la tabla se creó correctamente:
-- SELECT * FROM "TOMA_FISICA"."USUARIO_UBICACION";
-- 
-- Para verificar la estructura:
-- \d "TOMA_FISICA"."USUARIO_UBICACION"
