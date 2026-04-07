// ===================================================================================
// Módulo de utilidades para manejo de timezone y fecha/hora
// Optimizado para países de Latinoamérica (Centroamérica y Sudamérica)
// ===================================================================================

/**
 * Mapa de zonas horarias de Latinoamérica con información precisa
 * Incluye offset UTC, nombre del país, y si usa DST (horario de verano)
 */
const LATIN_AMERICA_TIMEZONES = {
    // Centroamérica - UTC-6 (sin DST)
    'America/Guatemala': { offset: -6, country: 'Guatemala', dst: false, display: 'CST (UTC-6)' },
    'America/El_Salvador': { offset: -6, country: 'El Salvador', dst: false, display: 'CST (UTC-6)' },
    'America/Tegucigalpa': { offset: -6, country: 'Honduras', dst: false, display: 'CST (UTC-6)' },
    'America/Managua': { offset: -6, country: 'Nicaragua', dst: false, display: 'CST (UTC-6)' },
    'America/Costa_Rica': { offset: -6, country: 'Costa Rica', dst: false, display: 'CST (UTC-6)' },
    'America/Belize': { offset: -6, country: 'Belice', dst: false, display: 'CST (UTC-6)' },
    
    // Panamá - UTC-5 (sin DST)
    'America/Panama': { offset: -5, country: 'Panamá', dst: false, display: 'UTC-5' },
    
    // Colombia - UTC-5 (sin DST)
    'America/Bogota': { offset: -5, country: 'Colombia', dst: false, display: 'UTC-5' },
    
    // Ecuador - UTC-5 (sin DST)
    'America/Guayaquil': { offset: -5, country: 'Ecuador', dst: false, display: 'UTC-5' },
    
    // Perú - UTC-5 (sin DST)
    'America/Lima': { offset: -5, country: 'Perú', dst: false, display: 'UTC-5' },
    
    // Venezuela - UTC-4 (sin DST)
    'America/Caracas': { offset: -4, country: 'Venezuela', dst: false, display: 'UTC-4' },
    
    // Bolivia - UTC-4 (sin DST)
    'America/La_Paz': { offset: -4, country: 'Bolivia', dst: false, display: 'UTC-4' },
    
    // Paraguay - UTC-4/-3 (con DST)
    'America/Asuncion': { offset: -4, country: 'Paraguay', dst: true, display: 'PYT (UTC-4/-3)' },
    
    // Chile - UTC-4/-3 (con DST)
    'America/Santiago': { offset: -4, country: 'Chile', dst: true, display: 'CLT (UTC-4/-3)' },
    
    // Argentina - UTC-3 (sin DST)
    'America/Argentina/Buenos_Aires': { offset: -3, country: 'Argentina', dst: false, display: 'ART (UTC-3)' },
    'America/Argentina/Cordoba': { offset: -3, country: 'Argentina', dst: false, display: 'ART (UTC-3)' },
    'America/Argentina/Mendoza': { offset: -3, country: 'Argentina', dst: false, display: 'ART (UTC-3)' },
    
    // Uruguay - UTC-3 (sin DST)
    'America/Montevideo': { offset: -3, country: 'Uruguay', dst: false, display: 'UYT (UTC-3)' },
    
    // Brasil (múltiples zonas)
    'America/Sao_Paulo': { offset: -3, country: 'Brasil', dst: false, display: 'BRT (UTC-3)' },
    'America/Manaus': { offset: -4, country: 'Brasil', dst: false, display: 'AMT (UTC-4)' },
    'America/Fortaleza': { offset: -3, country: 'Brasil', dst: false, display: 'BRT (UTC-3)' },
    'America/Recife': { offset: -3, country: 'Brasil', dst: false, display: 'BRT (UTC-3)' },
    'America/Cuiaba': { offset: -4, country: 'Brasil', dst: false, display: 'AMT (UTC-4)' },
    'America/Rio_Branco': { offset: -5, country: 'Brasil', dst: false, display: 'ACT (UTC-5)' },
    
    // México (múltiples zonas)
    'America/Mexico_City': { offset: -6, country: 'México', dst: true, display: 'CST (UTC-6/-5)' },
    'America/Cancun': { offset: -5, country: 'México', dst: false, display: 'EST (UTC-5)' },
    'America/Tijuana': { offset: -8, country: 'México', dst: true, display: 'PST (UTC-8/-7)' },
    'America/Monterrey': { offset: -6, country: 'México', dst: true, display: 'CST (UTC-6/-5)' },
    
    // República Dominicana - UTC-4 (sin DST)
    'America/Santo_Domingo': { offset: -4, country: 'República Dominicana', dst: false, display: 'AST (UTC-4)' },
    
    // Cuba - UTC-5/-4 (con DST)
    'America/Havana': { offset: -5, country: 'Cuba', dst: true, display: 'CST (UTC-5/-4)' },
    
    // Puerto Rico - UTC-4 (sin DST)
    'America/Puerto_Rico': { offset: -4, country: 'Puerto Rico', dst: false, display: 'AST (UTC-4)' }
};

/**
 * Obtiene la zona horaria del navegador del usuario
 * @returns {string} Zona horaria IANA (ej: 'America/Guatemala')
 */
export function getUserTimezone() {
    try {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    } catch (e) {
        return 'America/Guatemala'; // Fallback por defecto
    }
}

/**
 * Obtiene la zona horaria para incluir en requests al servidor
 * @returns {string} Zona horaria del usuario
 */
export function getTimezoneForRequest() {
    return getUserTimezone();
}

/**
 * Obtiene información detallada de la zona horaria actual
 * @returns {Object} Información de timezone (offset, país, DST, display)
 */
export function getTimezoneInfo() {
    const timezone = getUserTimezone();
    
    // Si está en el mapa de Latinoamérica, usar info específica
    if (LATIN_AMERICA_TIMEZONES[timezone]) {
        return {
            timezone: timezone,
            ...LATIN_AMERICA_TIMEZONES[timezone]
        };
    }
    
    // Fallback: calcular offset dinámicamente para cualquier otra zona
    try {
        const date = new Date();
        const offsetMinutes = date.getTimezoneOffset();
        const offsetHours = -offsetMinutes / 60;
        const offsetStr = offsetHours >= 0 ? `UTC+${offsetHours}` : `UTC${offsetHours}`;
        
        return {
            timezone: timezone,
            offset: offsetHours,
            country: 'Desconocido',
            dst: false,
            display: offsetStr
        };
    } catch (e) {
        return {
            timezone: 'America/Guatemala',
            offset: -6,
            country: 'Guatemala',
            dst: false,
            display: 'CST (UTC-6)'
        };
    }
}

/**
 * Obtiene el offset UTC actual considerando DST
 * @returns {number} Offset en horas (ej: -5, -6, -3)
 */
export function getCurrentUTCOffset() {
    const date = new Date();
    const offsetMinutes = date.getTimezoneOffset();
    return -offsetMinutes / 60;
}

/**
 * Obtiene una representación legible de la zona horaria
 * Optimizado para Latinoamérica, mostrando UTC offset preciso
 * @returns {string} Zona horaria formateada (ej: 'UTC-5', 'CST (UTC-6)')
 */
export function getTimezoneAbbreviation() {
    try {
        const timezone = getUserTimezone();
        const info = getTimezoneInfo();
        
        // Si está en el mapa de Latinoamérica, usar el display específico
        if (LATIN_AMERICA_TIMEZONES[timezone]) {
            return info.display;
        }
        
        // Para otras zonas, intentar obtener abreviatura nativa del navegador
        const date = new Date();
        const formatter = new Intl.DateTimeFormat('en-US', {
            timeZone: timezone,
            timeZoneName: 'short'
        });
        
        const parts = formatter.formatToParts(date);
        const tzPart = parts.find(part => part.type === 'timeZoneName');
        
        if (tzPart && tzPart.value) {
            return tzPart.value;
        }
        
        // Fallback: mostrar offset UTC
        const currentOffset = getCurrentUTCOffset();
        return currentOffset >= 0 ? `UTC+${currentOffset}` : `UTC${currentOffset}`;
        
    } catch (e) {
        // Último fallback
        const currentOffset = getCurrentUTCOffset();
        return currentOffset >= 0 ? `UTC+${currentOffset}` : `UTC${currentOffset}`;
    }
}

/**
 * Obtiene un display extendido con país y offset
 * @returns {string} Formato: "UTC-5 (Panamá)" o "CST (UTC-6) - Guatemala"
 */
export function getTimezoneDisplayExtended() {
    const info = getTimezoneInfo();
    return `${info.display} - ${info.country}`;
}

/**
 * Formatea una fecha en formato legible
 * @param {Date} date - Objeto Date a formatear
 * @param {Object} options - Opciones de formato
 * @returns {string} Fecha formateada
 */
export function formatDateTime(date = new Date(), options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: getUserTimezone()
    };
    
    const formatOptions = { ...defaultOptions, ...options };
    
    try {
        return new Intl.DateTimeFormat('es-GT', formatOptions).format(date);
    } catch (e) {
        // Fallback manual si falla Intl
        const pad = (n) => String(n).padStart(2, '0');
        return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }
}

/**
 * Obtiene la fecha y hora actual formateada
 * @returns {string} Fecha y hora actual en formato legible
 */
export function getCurrentDateTime() {
    return formatDateTime(new Date());
}

/**
 * Obtiene solo la fecha actual formateada
 * @returns {string} Fecha actual en formato DD/MM/YYYY
 */
export function getCurrentDate() {
    const date = new Date();
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        timeZone: getUserTimezone()
    };
    
    try {
        return new Intl.DateTimeFormat('es-GT', options).format(date);
    } catch (e) {
        const pad = (n) => String(n).padStart(2, '0');
        return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()}`;
    }
}

/**
 * Obtiene solo la hora actual formateada
 * @returns {string} Hora actual en formato HH:MM:SS
 */
export function getCurrentTime() {
    const date = new Date();
    const options = {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: getUserTimezone()
    };
    
    try {
        return new Intl.DateTimeFormat('es-GT', options).format(date);
    } catch (e) {
        const pad = (n) => String(n).padStart(2, '0');
        return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }
}

/**
 * Convierte una fecha string en formato DD/MM/YYYY a objeto Date
 * @param {string} dateString - Fecha en formato DD/MM/YYYY
 * @returns {Date|null} Objeto Date o null si el formato es inválido
 */
export function parseDateString(dateString) {
    if (!dateString || typeof dateString !== 'string') {
        return null;
    }
    
    const parts = dateString.trim().split('/');
    if (parts.length !== 3) {
        return null;
    }
    
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Meses en JS son 0-indexed
    const year = parseInt(parts[2], 10);
    
    if (isNaN(day) || isNaN(month) || isNaN(year)) {
        return null;
    }
    
    const date = new Date(year, month, day);
    
    // Validar que la fecha sea válida
    if (date.getDate() !== day || date.getMonth() !== month || date.getFullYear() !== year) {
        return null;
    }
    
    return date;
}

/**
 * Valida si una zona horaria es de Latinoamérica
 * @param {string} timezone - Zona horaria IANA
 * @returns {boolean} true si es de Latinoamérica
 */
export function isLatinAmericaTimezone(timezone = null) {
    const tz = timezone || getUserTimezone();
    return LATIN_AMERICA_TIMEZONES.hasOwnProperty(tz);
}

/**
 * Obtiene todas las zonas horarias de Latinoamérica
 * @returns {Array} Lista de objetos con info de cada zona
 */
export function getAllLatinAmericaTimezones() {
    return Object.entries(LATIN_AMERICA_TIMEZONES).map(([tz, info]) => ({
        timezone: tz,
        ...info
    }));
}
