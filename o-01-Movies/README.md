# Ontology #1: Movie Domain    
     
## Thought Framework for Building Ontologies
     
### General Methodology for Building Ontologies

1. **Define the Purpose and Scope**    
   - What do we want to capture about the domain?    
   - Who will use this ontology and for what tasks?

2. **Identify Core Concepts and Relationships**    
   - Brainstorm key entities.    
   - Decide how these entities relate to each other.

3. **Organize Hierarchies (Taxonomies) and Properties**    
   - Group similar concepts in hierarchies.    
   - Identify attributes (data properties) for each concept.    
   - Identify relationships (object properties) among concepts.

4. **Iterate and Refine**    
   - Create a first pass.    
   - Check for missing concepts, properties, or inconsistencies.    
   - Repeat until the ontology is stable enough to use.

5. **Validate with Sample Data**    
   - Create or collect sample data.    
   - Check if the ontology can capture the data properly.    
   - Adjust if needed.

6. **Document**    
   - Use a standard structure (e.g., RDF/OWL notations in practice).    
   - Make your ontology discoverable and understandable.

---
### A simple way to start    

**One way** to think of an ontology is in terms of everyday language constructs:

1. **Nouns → Classes / Entities**    
   These are the “things” in your domain (e.g., Movie, Actor, Director).    

2. **Verbs → Relationships / Object Properties**    
   These describe how nouns relate to each other (e.g., “Movie *has* Actor,” “Actor *portrays* Character,” “Movie *won* Award”).    

3. **Adjectives / Adverbs → Data Properties**    
   These describe or qualify our nouns or relationships (e.g., a Movie’s `title`, `releaseYear`, `rating`; an Actor’s `name`, `birthDate`; an Award’s `name`, `year`).    

Using this mental model helps keep things structured:    
- **Nouns (Classes)** are your domain’s main building blocks.    
- **Verbs (Relations)** connect your domain’s main building blocks.    
- **Adjectives (Data Properties)** give us descriptive detail about those blocks or relationships.    

--- 

## Creating Ontology #1: Movie Domain
    
#### Purpose & Scope

We will create a simple ontology about movies, capturing essential concepts like:    
- Movie titles    
- Genres    
- Actors    
- Directors    
- Characters    
- Release details  (optional)

This ontology might be used for:
* a basic movie catalog
* recommendation systems
* a reference system for users looking up movie information

#### Identify Core Concepts and Relationships

**Core Concepts (Classes):**
1. **Movie**: A cinematic film.
2. **Person**: Any individual involved in the movie. This can be specialized into:
   - **Actor**: A person who acts in movies.
   - **Director**: A person who directs movies.
3. **Character**: A fictional or real role portrayed in a movie.
4. **Genre**: A type/category of movies (e.g., Action, Drama, Comedy).

**Relationships (Object Properties)**:
1. `hasActor` (Movie -> Person) : indicates who acted in the movie.
2. `hasDirector` (Movie -> Person) : indicates who directed the movie.
3. `playsCharacter` (Actor -> Character) : indicates which character an actor portrayed.
4. `belongsToGenre` (Movie -> Genre) : indicates which genre(s) the movie belongs to.

**Data Properties** (attributes):
- **Movie**: `title` (string), `releaseYear` (integer), `duration` (integer, in minutes), `rating` (float, e.g., IMDB rating).
- **Person**: `name` (string), `birthDate` (date).
- **Character**: `name` (string).
- **Genre**: `name` (string).

#### Organize Hierarchies and Properties

The hierarchical part is fairly straightforward here:    
- **Person**    
  - **Actor**    
  - **Director**    

(Note from Object Oriented Programming: `Actor` and `Director` can be separate classes, but a typical approach is to keep them as sub-classes of `Person` to unify common properties such as name, birthDate, etc.)
    
Movies can be multi-genre, so we will allow one movie to link to multiple genres.  
  
---

## Alternative approach to creating Ontology #1: Movie Domain

### Identify Core Classes (Nouns)

1. **Movie**    
2. **Person** – a more general concept that can be specialized:
   - **Actor**
   - **Director**
3. **Character**    
4. **Genre**    

(Like before, we often subclass `Person` to represent specialized roles in movie-making. You could also include `Writer`, `Editor`, etc. for additional detail.)

### Identify Relationships (Verbs)    

1. **hasActor** (Movie → Actor)    
   - A movie has one or many actors.    

2. **hasDirector** (Movie → Director)    
   - A movie has one or many directors (though typically one primary, multiple are possible).    

3. **belongsToGenre** (Movie → Genre)    
   - A movie may belong to multiple genres.     

---    

## Outcome  
The structure of the final ontology is here: [o1-structure.md](https://github.com/shauryashaurya/The-Silmaril/blob/main/o-1/o1-structure.md)  
     
The accompanying notebook creates sample data for the ontology for you to import into a typical SQL database and perform analysis.

```mermaid                      
classDiagram    
    class Movie {    
        %% Data Properties    
        -title : string    
        -releaseYear : int    
        -duration : int    
        -rating : float    
        %% Object Properties    
        +hasActor o--* Actor : one-to-many    
        +hasDirector o--* Director : one-to-many    
        +belongsToGenre o--* Genre : one-to-many    
    }    
    
    class Person {    
        %% Data Properties    
        -name : string    
        -birthDate : date    
    }    
    
    class Actor {    
        %% Object Properties    
        +playsCharacter --o Character : one-to-one    
    }    
    
    class Director {    
        %% Inherited Data Properties from Person (name, birthDate) are implicitly present    
    }    
    note for Director "(no special object property here, but reuses name/birthDate)"    
    
    class Character {    
        %% Data Properties    
        -name : string    
    }    
    
    class Genre {    
        %% Data Properties    
        -name : string    
    }    
    
    Actor --|> Person    
    Director --|> Person    
	
	Movie "1" --> "1..*" Actor : Association (hasActor)
    Movie "1" --> "1..*" Director : Association (hasDirector)
    Movie "1" --> "1..*" Genre : Association (belongsToGenre)
    Actor "1" --> "1" Character : Association (playsCharacter)
```    

---  
  
## Thoughts

1. **Ontology as Grammar**:    
   - **Nouns** (Classes): Movie, Person, Character, etc.    
   - **Verbs** (Object Properties): hasActor, hasDirector, portraysCharacter, etc.    
   - **Adjectives** (Data Properties): `title`, `rating`, `name`, etc.

2. **Refinement**: We can continue to refine or expand:
   - **Add more roles** (Writers, Editors, Composers).    
   - **Add more complex relationships** (e.g., co-acting relationships between two actors).    
   - **Add cardinalities or restrictions** (e.g., a movie must have at least 1 director).

3. **Apply to Any Domain**: The same approach—brainstorming nouns, verbs, and descriptors—applies universally (e.g., Supply Chain, Insurance, Construction, Manufacturing). Always ask:    
   - **Which “things” (classes) do we need?**    
   - **How do those things interact or relate (relationships)?**    
   - **What descriptive attributes do they have (data properties)?**    
  
  
---

# Thinking about the reasoner  

So what pattern can we see in the reasoner?  
Let's map the overall flow of the reasoner...

```mermaid
graph TD
    %% Input Data Sources
    INPUT1[N3 Ontology File] --> PARSE1[parse_ontology_schema]
    INPUT2[CSV Dataset 1] --> LOAD1[load_csv_with_normalization]
    INPUT3[CSV Dataset 2] --> LOAD2[load_csv_with_normalization]
    INPUT4[CSV Dataset N] --> LOAD3[load_csv_with_normalization]
    
    %% Data Transformation Pipeline
    PARSE1 --> SCHEMA[Ontology Schema<br/>Classes, Properties, Rules]
    LOAD1 --> NORM1[normalize_ids_and_types]
    LOAD2 --> NORM2[normalize_ids_and_types]
    LOAD3 --> NORM3[normalize_ids_and_types]
    
    NORM1 --> ENTITIES[Entity Models<br/>Typed Objects]
    NORM2 --> ENTITIES
    NORM3 --> ENTITIES
    
    ENTITIES --> VALIDATE[validate_relationships<br/>Foreign Key Integrity]
    VALIDATE --> CLEAN_DATA[Clean Validated Data<br/>Ready for Reasoning]
    
    %% Reasoning Transformation
    CLEAN_DATA --> STATS[compute_basic_statistics<br/>Aggregations & Metrics]
    SCHEMA --> RULES[extract_reasoning_rules<br/>N3 → Python Logic]
    
    STATS --> APPLY_RULES[apply_reasoning_rules<br/>Classification & Inference]
    RULES --> APPLY_RULES
    
    APPLY_RULES --> ENRICHED[Enriched Entities<br/>+ Classification Properties]
    ENRICHED --> RELATIONSHIPS[build_relationship_mappings<br/>Similarities, Preferences]
    RELATIONSHIPS --> DERIVED[Derived Knowledge<br/>Recommendations, Segments]
    
    %% Multi-path Output Generation
    DERIVED --> ANALYTICS_PATH[Analytics Pipeline]
    DERIVED --> RDF_PATH[RDF Pipeline]
    DERIVED --> REPORT_PATH[Reporting Pipeline]
    
    %% Analytics Transformation
    ANALYTICS_PATH --> TRENDS[analyze_trends<br/>Statistical Insights]
    TRENDS --> SEGMENTS[create_segments<br/>User/Entity Groups]
    SEGMENTS --> RECOMMENDATIONS[generate_recommendations<br/>Personalized Suggestions]
    RECOMMENDATIONS --> INSIGHTS[extract_business_insights<br/>Actionable Intelligence]
    INSIGHTS --> JSON_OUT[analytics_results.json]
    
    %% RDF Transformation
    RDF_PATH --> RDF_CONVERT[convert_to_rdf_triples<br/>Entity → URI + Properties]
    RDF_CONVERT --> RDF_RELATIONS[add_relationship_triples<br/>Object Properties]
    RDF_RELATIONS --> RDF_REASONING[add_reasoning_annotations<br/>Derived Knowledge]
    RDF_REASONING --> RDF_VALIDATE[validate_rdf_consistency<br/>URI Integrity Check]
    RDF_VALIDATE --> MULTI_FORMAT[export_multiple_formats<br/>TTL, N3, JSON-LD, RDF/XML, NT]
    MULTI_FORMAT --> RDF_STATS[rdf_statistics.json/.txt]
    
    %% Reporting Transformation
    REPORT_PATH --> MD_SECTIONS[generate_report_sections<br/>Executive Summary, Analysis]
    MD_SECTIONS --> MD_TABLES[format_data_tables<br/>Markdown Tables]
    MD_TABLES --> MD_INSIGHTS[add_business_insights<br/>Strategic Recommendations]
    MD_INSIGHTS --> MD_OUT[analysis_report.md]
    
    %% Data Quality Monitoring (parallel stream)
    VALIDATE -.-> QC1[data_quality_checks]
    APPLY_RULES -.-> QC2[reasoning_quality_checks]
    RDF_VALIDATE -.-> QC3[rdf_quality_checks]
    
    QC1 --> QC_REPORT[quality_diagnostics.log]
    QC2 --> QC_REPORT
    QC3 --> QC_REPORT
    
    %% Styling for different data types
    classDef inputData fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef transformation fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef enrichedData fill:#fff8e1,stroke:#ef6c00,stroke-width:2px
    classDef outputData fill:#fce4ec,stroke:#ad1457,stroke-width:2px
    classDef qualityCheck fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px,stroke-dasharray: 3 3
    
    class INPUT1,INPUT2,INPUT3,INPUT4 inputData
    class PARSE1,LOAD1,LOAD2,LOAD3,NORM1,NORM2,NORM3,VALIDATE,STATS,APPLY_RULES,TRENDS,SEGMENTS,RECOMMENDATIONS,RDF_CONVERT,RDF_RELATIONS,RDF_REASONING,MD_SECTIONS,MD_TABLES transformation
    class SCHEMA,ENTITIES,CLEAN_DATA,ENRICHED,RELATIONSHIPS,DERIVED,INSIGHTS enrichedData
    class JSON_OUT,MULTI_FORMAT,RDF_STATS,MD_OUT outputData
    class QC1,QC2,QC3,QC_REPORT qualityCheck
```

Can we have a interface that shows the essential methods our ontology reasoner class should implement?
Based on our learnings:

## **Reasoner Interface: Core**

### **Phase 1: Initialization**
- `__init__(data_path)` - Setup with data location
- `configure_parameters()` - Set reasoning thresholds and options

### **Phase 2: Data Loading** 
- `load_data()` - Load all CSV datasets
- `normalize_entity_ids()` - Handle ID type mismatches
- `validate_data_integrity()` - Check foreign key relationships
- `diagnose_data_issues()` - Report data quality problems

### **Phase 3: Reasoning**
- `compute_basic_statistics()` - Calculate aggregations and metrics
- `apply_reasoning_rules()` - Execute all N3 reasoning rules
- `_rule_XX_methods()` - Individual rule implementations

### **Phase 4: Output**
- `generate_report()` - Create summary of reasoning results
- `export_reasoning_results()` - Save basic outputs

## **Reasoner Interface: Extensions (Optional)**

### **Analytics Extension**
- `analyze_distributions()` - Statistical analysis
- `compute_trends()` - Pattern identification  
- `generate_recommendations()` - Suggestion algorithms
- `export_analytics_json()` - Structured data export
- `generate_markdown_report()` - Human-readable reports

### **RDF Extension**
- `load_ontology_schema()` - Parse N3 ontology files
- `convert_entities_to_rdf()` - Transform to semantic triples
- `export_multiple_formats()` - TTL, N3, JSON-LD, etc.
- `generate_rdf_statistics()` - RDF-specific metrics

## Simplified flow:

```mermaid
graph TD
    %% Core Reasoner Essential Interface
    subgraph "Core Reasoner Interface"
        %% Initialization Phase
        INIT["`**INITIALIZATION**
        __init__(data_path)
        configure_parameters()`"]
        
        %% Data Loading Phase  
        DATA["`**DATA LOADING**
        load_data()
        normalize_entity_ids()
        validate_data_integrity()
        diagnose_data_issues()`"]
        
        %% Reasoning Phase
        REASON["`**REASONING**
        compute_basic_statistics()
        apply_reasoning_rules()
        _rule_XX_methods()`"]
        
        %% Output Phase
        OUTPUT["`**OUTPUT**
        generate_report()
        export_reasoning_results()`"]
    end
    
    %% Analytics Extension Interface
    subgraph "Analytics Extension Interface"
        ANALYTICS["`**ANALYTICS**
        analyze_distributions()
        compute_trends()
        generate_recommendations()
        export_analytics_json()
        generate_markdown_report()`"]
    end
    
    %% RDF Extension Interface
    subgraph "RDF Extension Interface"
        RDF["`**RDF MANAGEMENT**
        load_ontology_schema()
        convert_entities_to_rdf()
        export_multiple_formats()
        generate_rdf_statistics()`"]
    end
    
    %% Flow
    INIT --> DATA
    DATA --> REASON
    REASON --> OUTPUT
    
    %% Extensions depend on core
    OUTPUT -.->|extends| ANALYTICS
    OUTPUT -.->|extends| RDF
    
    %% Styling
    classDef corePhase fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef extensionPhase fill:#f1f8e9,stroke:#388e3c,stroke-width:2px
    
    class INIT,DATA,REASON,OUTPUT corePhase
    class ANALYTICS,RDF extensionPhase
```
