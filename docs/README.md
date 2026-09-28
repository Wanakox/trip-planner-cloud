# TripPlanner Documentation

This directory contains the analysis, architecture, design, diagrams, reference material and official project documents associated with TripPlanner.

The documentation is organized by purpose so that requirements, design artifacts and supporting material remain separated from the source code.

---

## Directory Structure

```text
docs/
├── analysis/
├── architecture/
├── design/
├── diagrams/
├── references/
├── requirements/
└── README.md
```

---

## `analysis/`

Contains the documentation produced during the requirements analysis phase.

```text
analysis/
├── requirements-extraction.txt
├── TripPlanner - Analisis.pdf
└── TripPlanner - Matriz de trazabilidad.pdf
```

### Files

#### `requirements-extraction.txt`

Initial working document used to extract, collect and refine the system requirements.

This file contains preliminary information used before producing the final analysis document. It is kept as supporting evidence of the requirements engineering process.

#### `TripPlanner - Analisis.pdf`

Main system analysis document.

It includes:

- Functional requirements
- Non-functional requirements
- MoSCoW requirement prioritization
- Primary and secondary actors
- Use-case definitions
- Detailed use-case specifications
- Main flows
- Alternative flows
- Preconditions
- Postconditions
- Use-case diagram

This document defines the expected behavior and functional scope of TripPlanner before implementation.

#### `TripPlanner - Matriz de trazabilidad.pdf`

Requirements traceability matrix.

It establishes the relationship between functional requirements and use cases, making it possible to verify that every requirement is covered by at least one system interaction.

The matrix is used to:

- Check requirement coverage
- Detect missing use cases
- Support testing
- Track changes during implementation
- Maintain consistency between analysis and development

---

## `architecture/`

Contains the architectural description of the system.

```text
architecture/
└── architecture.md
```

### `architecture.md`

Describes the high-level architecture selected for TripPlanner.

The document explains the main system components and the communication between them, including:

- React and TypeScript frontend
- FastAPI backend
- PostgreSQL database
- Redis
- RQ background workers
- REST API communication
- Docker-based deployment
- Raspberry Pi 5 deployment environment
- External services and integrations

This document should remain focused on the architectural structure of the system rather than detailed implementation decisions.

---

## `design/`

Contains the detailed software design documentation.

```text
design/
└── TripPlanner - Diseño.pdf
```

### `TripPlanner - Diseño.pdf`

Main system design document.

It includes:

- System architecture
- Entity classes
- Control classes
- External service classes
- Class specifications
- Initial class diagram
- Refined class diagram
- Entity-relationship diagram
- Activity diagrams
- API design
- Database design information
- Relationships between system components

This document serves as the bridge between the analysis phase and the implementation phase.

The design may be adjusted during development when implementation constraints or technical decisions require changes. Any relevant modification should remain consistent with the requirements defined in the analysis documentation.

---

## `diagrams/`

Contains the graphical representations produced during the analysis and design phases.

```text
diagrams/
├── arquitectura_sistema.png
├── Diagrama CU.png
├── Diagrama de actividad/
├── Diagrama de clases/
├── Diagrama E-R.png
└── EDT.png
```

### `arquitectura_sistema.png`

Graphical representation of the physical and logical system architecture.

It shows the main components of TripPlanner, including:

- Web client
- Frontend container
- Backend API
- PostgreSQL
- Redis
- RQ worker
- External services
- Docker deployment environment
- Raspberry Pi server

### `Diagrama CU.png`

UML use-case diagram.

It represents:

- Registered and unregistered users
- Main system functionalities
- External actors
- Relationships between use cases
- Includes and extension points

The diagram provides a global view of how users interact with TripPlanner.

### `Diagrama de actividad/`

Contains the activity diagrams associated with the system use cases.

```text
Diagrama de actividad/
├── DA - 1.png
├── DA - 2.png
├── ...
└── DA - 30.png
```

Each diagram represents the workflow of one use case.

The numbering corresponds to the use-case identifiers:

| Diagram | Use case |
|---|---|
| `DA - 1.png` | Register user |
| `DA - 2.png` | Log in |
| `DA - 3.png` | View profile |
| `DA - 4.png` | Edit profile |
| `DA - 5.png` | Log out |
| `DA - 6.png` | Delete account |
| `DA - 7.png` | Create trip |
| `DA - 8.png` | Edit trip |
| `DA - 9.png` | Delete trip |
| `DA - 10.png` | View trip details |
| `DA - 11.png` | Search trip |
| `DA - 12.png` | Add activity |
| `DA - 13.png` | Delete activity |
| `DA - 14.png` | Edit activity |
| `DA - 15.png` | Mark activity as completed |
| `DA - 16.png` | Move activity |
| `DA - 17.png` | Add task |
| `DA - 18.png` | Delete task |
| `DA - 19.png` | Edit task |
| `DA - 20.png` | Reorder task |
| `DA - 21.png` | Mark task as completed |
| `DA - 22.png` | Add file |
| `DA - 23.png` | Delete file |
| `DA - 24.png` | Add note |
| `DA - 25.png` | Delete note |
| `DA - 26.png` | Edit note |
| `DA - 27.png` | Export trip information |
| `DA - 28.png` | Synchronize Google Calendar |
| `DA - 29.png` | Add Google Calendar event |
| `DA - 30.png` | Search flights |

These diagrams describe decisions, validations, alternative paths and system responses for each interaction.

### `Diagrama de clases/`

Contains the UML class diagrams.

```text
Diagrama de clases/
├── Diagrama de Clases.png
└── Diagrama de Clases Refinado.png
```

#### `Diagrama de Clases.png`

Initial class diagram created from the system analysis.

It identifies the main:

- Entity classes
- Control classes
- External service classes
- Attributes
- Operations
- Relationships

#### `Diagrama de Clases Refinado.png`

Refined implementation-oriented class diagram.

It expands the initial class model by defining:

- Attribute visibility
- Method visibility
- Data types
- Method parameters
- Return types
- Multiplicities
- Associations
- Aggregations
- Compositions
- Dependencies

This diagram provides a more precise reference for implementing the backend domain and service layers.

### `Diagrama E-R.png`

Entity-relationship diagram for the PostgreSQL database.

It represents:

- Persistent entities
- Primary keys
- Foreign keys
- Attributes
- Cardinalities
- Relationships
- Referential constraints

This diagram is the conceptual basis for implementing the relational database model.

### `EDT.png`

Work Breakdown Structure diagram.

It divides the project into manageable work packages, including:

- Requirements analysis
- Software design
- Database implementation
- Backend implementation
- API development
- Frontend development
- Testing
- Integration
- Deployment
- Documentation

The diagram is used to define the project scope and organize the development work.

---

## `references/`

Contains academic and technical reference material used during the analysis and design of TripPlanner.

```text
references/
├── DCS.pdf
├── MDAS.pdf
└── Presentación_defensa_p1y2.pdf
```

### `DCS.pdf`

Reference material related to software design and construction.

It was used as supporting material for concepts such as:

- Object-oriented design
- UML diagrams
- Class modeling
- Relationships between classes
- Software architecture
- Design refinement

### `MDAS.pdf`

Reference material related to advanced software modeling and design.

It supports the application of:

- Clean Code
- SOLID principles
- Design quality
- Modularity
- Maintainability
- Separation of responsibilities

### `Presentación_defensa_p1y2.pdf`

Reference presentation related to the preparation or structure of the Final Degree Project defense.

It is stored as supporting material and is not part of the TripPlanner system specification.

Files in this directory are external references and should not be treated as authoritative TripPlanner requirements or design documents.

---

## `requirements/`

Contains official and administrative documents related to the Final Degree Project.

```text
requirements/
├── AnexoIII_JuanGarcia_signed.pdf
└── PeticionTemaJuanGarcia.pdf
```

### `PeticionTemaJuanGarcia.pdf`

Initial Final Degree Project proposal.

It defines:

- Project title
- Motivation
- Main objective
- Specific objectives
- Project description
- Project phases
- Work Breakdown Structure
- Estimated schedule
- Required resources
- Technology selection
- Expected documentation

This document establishes the original scope and academic context of TripPlanner.

### `AnexoIII_JuanGarcia_signed.pdf`

Signed official document associated with the approval or registration of the Final Degree Project.

It is retained as administrative evidence and is not part of the technical system specification.

---

## Documentation Relationships

The documentation follows this general flow:

```text
Project proposal
       |
       v
Requirements extraction
       |
       v
System analysis
       |
       v
Traceability matrix
       |
       v
System architecture
       |
       v
Detailed design
       |
       v
Implementation
       |
       v
Testing and validation
```

The documents have different responsibilities:

| Document | Main purpose |
|---|---|
| Project proposal | Define the original project scope and objectives |
| Requirements extraction | Capture and refine initial requirements |
| Analysis document | Define system behavior and use cases |
| Traceability matrix | Relate requirements to use cases |
| Architecture document | Describe the high-level technical structure |
| Design document | Define classes, data model, workflows and implementation guidance |
| Diagrams | Provide graphical representations of analysis and design decisions |
| References | Support the methodology and technical decisions |

---

## Documentation Maintenance

The documentation should be updated when implementation decisions affect the designed system.

The following rules should be followed:

1. Functional changes must be reflected in the analysis document.
2. Database changes must be reflected in the entity-relationship diagram.
3. Structural backend changes must be reflected in the class or architecture documentation when relevant.
4. New use cases must be added to the traceability matrix.
5. Removed requirements must not remain mapped to active use cases.
6. Generated diagrams should remain synchronized with their editable source files.
7. Duplicate documents should be avoided unless there is a justified canonical and exported version.
8. Administrative documents should not be modified.
9. Reference documents should not be presented as project-specific specifications.

---

## Naming Conventions

The current files preserve the original names used during the analysis and design phases.

For future documentation, the recommended naming convention is:

```text
lowercase-kebab-case
```

Examples:

```text
system-architecture.png
use-case-diagram.png
entity-relationship-diagram.png
refined-class-diagram.png
traceability-matrix.pdf
```

Avoid spaces, accents and inconsistent capitalization in new file names because they complicate:

- Terminal commands
- Markdown links
- Shell scripts
- Docker configuration
- Automated documentation generation

Existing files may be renamed progressively while keeping all internal Markdown links updated.

---

## Source of Truth

When inconsistencies appear between documents, use the following priority order:

1. Approved project scope
2. Latest analysis documentation
3. Traceability matrix
4. Latest design documentation
5. Individual diagrams
6. Preliminary extraction files
7. External reference material

The implementation should remain consistent with the latest approved analysis and design decisions.
