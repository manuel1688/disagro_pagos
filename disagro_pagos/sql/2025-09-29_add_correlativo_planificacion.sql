-- Migración: agregar correlativo a planificaciones y tabla de secuencias
-- Fecha: 2025-09-29

-- Añadir columnas a TOMA_FISICA.PLANIFICACION (idempotente)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'TOMA_FISICA'
      AND table_name = 'PLANIFICACION'
      AND column_name = 'CORRELATIVO'
  ) THEN
    ALTER TABLE "TOMA_FISICA"."PLANIFICACION"
      ADD COLUMN "CORRELATIVO" VARCHAR(120);
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'TOMA_FISICA'
      AND table_name = 'PLANIFICACION'
      AND column_name = 'CORRELATIVO_BASE'
  ) THEN
    ALTER TABLE "TOMA_FISICA"."PLANIFICACION"
      ADD COLUMN "CORRELATIVO_BASE" VARCHAR(60);
  END IF;
END $$;

-- Índices útiles (idempotentes)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_planificacion_correlativo'
      AND n.nspname = 'TOMA_FISICA'
  ) THEN
    CREATE INDEX idx_planificacion_correlativo
      ON "TOMA_FISICA"."PLANIFICACION" ("CORRELATIVO");
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_planificacion_correlativo_base'
      AND n.nspname = 'TOMA_FISICA'
  ) THEN
    CREATE INDEX idx_planificacion_correlativo_base
      ON "TOMA_FISICA"."PLANIFICACION" ("CORRELATIVO_BASE");
  END IF;
END $$;

-- Tabla de secuencias para correlativos (idempotente)
CREATE TABLE IF NOT EXISTS "TOMA_FISICA"."SECUENCIA_CORRELATIVO" (
  "PAIS" VARCHAR(10) NOT NULL,
  "BASE" VARCHAR(60) NOT NULL,
  "ANIO" INTEGER NOT NULL,
  "ULTIMO_CONSECUTIVO" INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT "PK_SECUENCIA_CORRELATIVO" PRIMARY KEY ("PAIS","BASE","ANIO")
);

-- Función para obtener el siguiente consecutivo de forma atómica
CREATE OR REPLACE FUNCTION "TOMA_FISICA".siguiente_correlativo(p_pais VARCHAR, p_base VARCHAR, p_anio INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE v_next INTEGER;
BEGIN
  LOOP
    UPDATE "TOMA_FISICA"."SECUENCIA_CORRELATIVO"
      SET "ULTIMO_CONSECUTIVO" = "ULTIMO_CONSECUTIVO" + 1
      WHERE "PAIS" = p_pais AND "BASE" = p_base AND "ANIO" = p_anio
      RETURNING "ULTIMO_CONSECUTIVO" INTO v_next;

    IF FOUND THEN
      RETURN v_next;
    END IF;

    BEGIN
      INSERT INTO "TOMA_FISICA"."SECUENCIA_CORRELATIVO" ("PAIS","BASE","ANIO","ULTIMO_CONSECUTIVO")
      VALUES (p_pais, p_base, p_anio, 1);
      RETURN 1;
    EXCEPTION WHEN unique_violation THEN
      -- Otro proceso creó la fila primero; reintentar el LOOP
    END;
  END LOOP;
END $$;

