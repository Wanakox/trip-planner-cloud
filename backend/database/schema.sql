-- TripPlanner - Modelo relacional inicial
-- Basado en el diagrama E-R.
-- PostgreSQL 17

DROP TABLE IF EXISTS
    actividad,
    transporte,
    gasto,
    participante,
    alojamiento,
    nota,
    archivo,
    tarea,
    destino,
    viaje,
    usuario
CASCADE;

BEGIN;

CREATE TABLE usuario (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    foto_perfil VARCHAR(500),
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    correo_electronico VARCHAR(255) NOT NULL UNIQUE,
    moneda_predeterminada CHAR(3) NOT NULL DEFAULT 'EUR',
    contrasena_hash VARCHAR(255) NOT NULL,

    CONSTRAINT ck_usuario_nombre_no_vacio CHECK (BTRIM(nombre) <> ''),
    CONSTRAINT ck_usuario_apellido_no_vacio CHECK (BTRIM(apellido) <> ''),
    CONSTRAINT ck_usuario_nombre_usuario_no_vacio CHECK (BTRIM(nombre_usuario) <> ''),
    CONSTRAINT ck_usuario_correo_no_vacio CHECK (BTRIM(correo_electronico) <> ''),
    CONSTRAINT ck_usuario_moneda_longitud CHECK (CHAR_LENGTH(moneda_predeterminada) = 3)
);

CREATE TABLE viaje (
    id BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    origen VARCHAR(150) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    descripcion TEXT,
    presupuesto NUMERIC(12, 2),
    moneda CHAR(3) NOT NULL,
    valoracion SMALLINT,
    estado VARCHAR(30) NOT NULL,

    CONSTRAINT fk_viaje_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT ck_viaje_nombre_no_vacio CHECK (BTRIM(nombre) <> ''),
    CONSTRAINT ck_viaje_fechas CHECK (fecha_fin >= fecha_inicio),
    CONSTRAINT ck_viaje_presupuesto CHECK (presupuesto IS NULL OR presupuesto >= 0),
    CONSTRAINT ck_viaje_moneda_longitud CHECK (CHAR_LENGTH(moneda) = 3),
    CONSTRAINT ck_viaje_valoracion CHECK (valoracion IS NULL OR valoracion BETWEEN 1 AND 5)
);

CREATE TABLE destino (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    pais VARCHAR(100) NOT NULL,
    ciudad VARCHAR(120) NOT NULL,
    orden INTEGER NOT NULL,
    moneda CHAR(3) NOT NULL,

    CONSTRAINT fk_destino_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT uq_destino_viaje_orden UNIQUE (id_viaje, orden),
    CONSTRAINT ck_destino_orden CHECK (orden > 0),
    CONSTRAINT ck_destino_moneda_longitud CHECK (CHAR_LENGTH(moneda) = 3)
);

CREATE TABLE tarea (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    orden INTEGER NOT NULL,
    prioridad VARCHAR(20) NOT NULL,
    completado BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_tarea_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT uq_tarea_viaje_orden UNIQUE (id_viaje, orden),
    CONSTRAINT ck_tarea_nombre_no_vacio CHECK (BTRIM(nombre) <> ''),
    CONSTRAINT ck_tarea_orden CHECK (orden > 0)
);

CREATE TABLE archivo (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    ruta VARCHAR(1000) NOT NULL,
    extension VARCHAR(20) NOT NULL,
    tamano BIGINT NOT NULL,

    CONSTRAINT fk_archivo_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT ck_archivo_nombre_no_vacio CHECK (BTRIM(nombre) <> ''),
    CONSTRAINT ck_archivo_tamano CHECK (tamano >= 0)
);

CREATE TABLE nota (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    texto TEXT NOT NULL,
    num_dia INTEGER NOT NULL,

    CONSTRAINT fk_nota_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT ck_nota_titulo_no_vacio CHECK (BTRIM(titulo) <> ''),
    CONSTRAINT ck_nota_num_dia CHECK (num_dia > 0)
);

CREATE TABLE alojamiento (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    direccion VARCHAR(250) NOT NULL,
    fecha_checkin DATE NOT NULL,
    fecha_checkout DATE NOT NULL,
    hora_checkin TIME,
    hora_checkout TIME,
    precio NUMERIC(12, 2),

    CONSTRAINT fk_alojamiento_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,

    CONSTRAINT ck_alojamiento_nombre_no_vacio CHECK (
        BTRIM(nombre) <> ''
    ),

    CONSTRAINT ck_alojamiento_direccion_no_vacia CHECK (
        BTRIM(direccion) <> ''
    ),

    CONSTRAINT ck_alojamiento_fechas CHECK (
        fecha_checkout >= fecha_checkin
    ),

    CONSTRAINT ck_alojamiento_horas CHECK (
        fecha_checkout <> fecha_checkin
        OR hora_checkin IS NULL
        OR hora_checkout IS NULL
        OR hora_checkout >= hora_checkin
    ),

    CONSTRAINT ck_alojamiento_precio CHECK (
        precio IS NULL
        OR precio >= 0
    )
);

CREATE TABLE participante (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    nombre VARCHAR(150) NOT NULL,

    CONSTRAINT fk_participante_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT ck_participante_nombre_no_vacio CHECK (BTRIM(nombre) <> '')
);

CREATE TABLE gasto (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    id_participante BIGINT NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    cantidad NUMERIC(12, 2) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    moneda CHAR(3) NOT NULL,
    fecha DATE NOT NULL,

    CONSTRAINT fk_gasto_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT fk_gasto_participante FOREIGN KEY (id_participante)
        REFERENCES participante(id) ON DELETE CASCADE,
    CONSTRAINT ck_gasto_nombre_no_vacio CHECK (BTRIM(nombre) <> ''),
    CONSTRAINT ck_gasto_cantidad CHECK (cantidad >= 0),
    CONSTRAINT ck_gasto_moneda_longitud CHECK (CHAR_LENGTH(moneda) = 3)
);

CREATE TABLE transporte (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    precio NUMERIC(12, 2),
    fecha_salida DATE NOT NULL,
    fecha_llegada DATE,
    hora_salida TIME,
    hora_llegada TIME,
    origen VARCHAR(200) NOT NULL,
    destino VARCHAR(200) NOT NULL,
    fecha_checkin DATE,

    CONSTRAINT fk_transporte_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,

    CONSTRAINT ck_transporte_fechas CHECK (
        fecha_llegada IS NULL
        OR fecha_llegada >= fecha_salida
    ),

    CONSTRAINT ck_transporte_precio CHECK (
        precio IS NULL
        OR precio >= 0
    ),

    CONSTRAINT ck_transporte_checkin CHECK (
        fecha_checkin IS NULL
        OR fecha_checkin <= fecha_salida
    ),

    CONSTRAINT ck_transporte_horas CHECK (
        fecha_llegada IS NULL
        OR fecha_llegada <> fecha_salida
        OR hora_salida IS NULL
        OR hora_llegada IS NULL
        OR hora_llegada >= hora_salida
    )
);

CREATE TABLE actividad (
    id BIGSERIAL PRIMARY KEY,
    id_viaje BIGINT NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    ubicacion VARCHAR(500),
    completado BOOLEAN NOT NULL DEFAULT FALSE,
    num_dia INTEGER NOT NULL,
    orden INTEGER NOT NULL,
    hora TIME,

    CONSTRAINT fk_actividad_viaje FOREIGN KEY (id_viaje)
        REFERENCES viaje(id) ON DELETE CASCADE,
    CONSTRAINT uq_actividad_viaje_dia_orden UNIQUE (id_viaje, num_dia, orden),
    CONSTRAINT ck_actividad_nombre_no_vacio CHECK (BTRIM(nombre) <> ''),
    CONSTRAINT ck_actividad_num_dia CHECK (num_dia > 0),
    CONSTRAINT ck_actividad_orden CHECK (orden > 0)
);

CREATE INDEX ix_viaje_id_usuario ON viaje(id_usuario);
CREATE INDEX ix_destino_id_viaje ON destino(id_viaje);
CREATE INDEX ix_tarea_id_viaje ON tarea(id_viaje);
CREATE INDEX ix_archivo_id_viaje ON archivo(id_viaje);
CREATE INDEX ix_nota_id_viaje ON nota(id_viaje);
CREATE INDEX ix_alojamiento_id_viaje ON alojamiento(id_viaje);
CREATE INDEX ix_participante_id_viaje ON participante(id_viaje);
CREATE INDEX ix_gasto_id_viaje ON gasto(id_viaje);
CREATE INDEX ix_gasto_id_participante ON gasto(id_participante);
CREATE INDEX ix_transporte_id_viaje ON transporte(id_viaje);
CREATE INDEX ix_actividad_id_viaje ON actividad(id_viaje);

-- El diagrama limita cada viaje a un máximo de 10 archivos.
CREATE OR REPLACE FUNCTION comprobar_limite_archivos_viaje()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM archivo
        WHERE id_viaje = NEW.id_viaje
    ) >= 10 THEN
        RAISE EXCEPTION 'Un viaje no puede almacenar más de 10 archivos';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_limite_archivos_viaje
BEFORE INSERT ON archivo
FOR EACH ROW
EXECUTE FUNCTION comprobar_limite_archivos_viaje();

COMMIT;