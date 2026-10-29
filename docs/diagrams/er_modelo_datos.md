# Diagrama Entidad-Relación — Modelo de Datos (Anexo C)

Modelo de las siete entidades principales del sistema (`tab:entidades`) en la
configuración entregada (release `v1.2.5`), verificado contra `App/Backend/app/models/`. Las tablas auxiliares
(`incidente_evento`, `incidente_comentario`, `telefonia_ingreso`, etc.) quedan
fuera del alcance de este diagrama.

```mermaid
erDiagram
    SECTOR ||--o{ INCIDENTE : "sector responsable"
    ESTADO ||--o{ INCIDENTE : "estado actual"
    CANAL_ORIGEN ||--o{ INCIDENTE : "medio de ingreso"
    INCIDENTE ||--o{ CLASIFICACION_LOG : "historial de decisiones"
    SECTOR ||--o{ CLASIFICACION_LOG : "sector predicho / validado"
    SECTOR ||--o{ DIRECTORIO_EMPLEADO : "sector de pertenencia"
    USERS ||--o{ DIRECTORIO_EMPLEADO : "credenciales vinculadas"
    DIRECTORIO_EMPLEADO ||--o{ INCIDENTE : "reportante"

    INCIDENTE {
        int id PK
        text descripcion_original "cifrada at-rest"
        text descripcion_pseudonimizada
        string prioridad
        int sector_id FK
        int estado_id FK
        int canal_origen_id FK
        int reportante_empleado_id FK
        bool requiere_revision_humana
    }
    SECTOR {
        int id PK
        string nombre
        string descripcion
    }
    ESTADO {
        int id PK
        string nombre
        bool es_terminal
    }
    CANAL_ORIGEN {
        int id PK
        string nombre
        string descripcion
    }
    CLASIFICACION_LOG {
        int id PK
        int incidente_id FK
        int sector_id_predicho FK
        int sector_id_validado FK
        numeric confianza
        string etapa
        bool requiere_revision_humana
    }
    USERS {
        int id PK
        string username
        string hashed_password
        bool is_active
    }
    DIRECTORIO_EMPLEADO {
        int id PK
        string legajo
        string nombre
        string email "cifrado Fernet (c-153)"
        string telefono "cifrado Fernet (c-153)"
        string email_bidx UK "indice ciego"
        string telefono_bidx "indice ciego"
        int sector_id FK
        int user_id FK
        string rol
        bool activo
        date fecha_baja
    }
```
