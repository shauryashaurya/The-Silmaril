# Ontology #2: Modelling the Music Domain
  

## Competency Questions Approach

**Key idea**: Start by asking, “What do we want our knowledge base to answer?” Then derive your ontology (classes, relationships, attributes) from these questions.  

For example, for the *music domain*, our competency questions could be:  
1. “Which songs are on which album?”  
2. “What is the genre of each album or song?”  
3. “Which artist performed each song?”  
4. “Which artist is signed to which label?”  
5. “When was a given album released?”  
6. “What is the duration of each song?”  
7. “Which songs have won any awards?”  

From these questions, we identify our domain’s classes, properties, and data properties that help us answer them.

---

### Purpose & Scope
A knowledge representation for songs, artists, albums, record labels, awards, and genres, sufficient to answer the competency questions.

### Key Classes (Step Derived from Competency Questions)
- **Song**  
- **Artist**  
- **Album**  
- **RecordLabel**  
- **Genre**  
- **Award**

### Relationships (Object Properties)
- `performedBy` (Song → Artist)  
- `featuredOn` (Song → Album)  
- `hasGenre` (Song → Genre) or (Album → Genre) – we’ll track both so that we can say an album can have a broad genre, and each song can be more specific.  
- `signedTo` (Artist → RecordLabel)  
- `hasWonAward` (Song → Award) – to track if a particular song won any awards.  

*(You could also store awards at the artist level if relevant, but for this example we focus on songs that win awards.)*  

### Data Properties
- **Song**: `title` (string), `duration` (integer in seconds), `releaseDate` (date)  
- **Artist**: `name` (string), `birthDate` (date) – optional for older artists, `nationality` (string)  
- **Album**: `album_title` (string), `releaseYear` (integer)  
- **RecordLabel**: `label_name` (string), `location` (string)  
- **Genre**: `genre_name` (string), `description` (string) – optional descriptive text  
- **Award**: `award_name` (string), `year` (integer), `awarding_body` (string)
    
---  
    
## Outcome  
The structure of the final ontology is here: [o2-structure.md](https://github.com/shauryashaurya/The-Silmaril/blob/main/o-02/o2-structure.md)  
     
The accompanying notebook creates sample data for the ontology for you to import and analyze.
  
```mermaid                                      
classDiagram                
    class Song {        
		%% Data Properties    
        -title : string                
        -duration : int                
        -releaseDate : date        
		%% Object Properties    
        +performedBy 1--* Artist : one-to-many                
        +featuredOn o--1 Album  : one-to-one               
        +hasGenre 1--* Genre  : one-to-many               
        +hasWonAward o--1 Award   : one-to-many              
    }                
                
    class Artist {                
		%% Data Properties    
        -name : string                
        -birthDate : date                
        -nationality : string                
		%% Object Properties    
        +signedTo o--1 RecordLabel                
    }                
                
    class Album {                
		%% Data Properties    
        -album_title : string                
        -releaseYear : int                
		%% Object Properties    
        +hasGenre *--1 Genre                
    }                
                
  class RecordLabel{                
		%% Data Properties    
        -label_name : string                
        -location : string                
  }                
                
    class Genre {                
		%% Data Properties    
        -genre_name : string                
        -description : string                
    }                
                
  class Award{                
		%% Data Properties    
        -award_name : string                
        -year : int                
        -awarding_body : string                
  }                
                
  class Single{                
		%% Data Properties    
		-isStandalone : boolean                
  }                
                
  class ExtendedPlay{                
		%% Data Properties    
		-numberOfTracks : int                
  }                
                
    Song "1" --> "*" Artist : Association (performedBy)    
    Song "1" --> "*" Album : Association (featuredOn)    
    Song "1" --> "*" Genre : Association (hasGenre)    
    Song "1" --> "*" Award : Association (hasWonAward)    
    Artist "1" --> "1" RecordLabel : Association (signedTo)    
    Album "1" --> "*" Genre : Association (hasGenre)    
    Album "1" --> "*" Artist : Association (releasedBy)    
    Album "1" --> "1" RecordLabel : Association (releasedBy)    
    Artist "1" --> "*" Award : Association (hasWonAward)    
        
    Single --|> Song : Inheritance    
    ExtendedPlay --|> Album : Inheritance               
```                    


---

# Thoughts

We used a different approach (the **Competency Questions** approach) to engineer this Ontology, we did not model the *entire* music domain, but just a subset of the *music business*, based on some questions that we needed answers to.    
    
	
# Reasoner

Let's think through the reasoner again here. 

This is approximately the flow that we followed:

```mermaid
graph TD
    A[initialize_reasoner_engine] --> B[load_entity_definitions]
    B --> C[load_base_entities]
    C --> D[load_central_hub_entities]
    D --> E[parse_embedded_relationships]
    
    E --> F[PHASE_1_build_inverse_relationships]
    F --> G[validate_foreign_key_integrity]
    G --> H[PHASE_2_build_derived_relationships]
    
    H --> I[validate_cardinality_constraints]
    I --> J[generate_loading_diagnostics]
    J --> K[validate_minimum_data_requirements]
    
    K --> L{data_sufficient}
    L -->|No| M[log_issues_and_exit]
    L -->|Yes| N[apply_reasoning_rules_by_category]
    
    N --> N1[category_1_basic_classification]
    N1 --> N2[category_2_inheritance_propagation]
    N2 --> N3[category_3_success_classification]
    N3 --> N4[category_4_network_analysis]
    N4 --> N5[category_5_quantitative_metrics]
    N5 --> N6[category_6_temporal_analysis]
    
    N6 --> O[update_inference_statistics]
    O --> P[generate_reasoning_diagnostics]
    
    P --> Q{output_required}
    
    Q -->|Analytics| R[initialize_analytics_engine]
    R --> S[generate_comprehensive_statistics]
    S --> T[extract_business_insights]
    T --> U[create_structured_reports]
    U --> AA[complete_analysis_pipeline]
    
    Q -->|RDF| V[initialize_rdf_manager]
    V --> W[convert_entities_to_rdf_triples]
    W --> X[convert_reasoning_results_to_rdf]
    X --> Y[validate_rdf_graph_consistency]
    Y --> Z[export_multiple_formats]
    Z --> BB[complete_rdf_export]
    
    Q -->|None| CC[complete_core_reasoning]
    
    classDef phase1 fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef phase2 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef reasoning fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef analytics fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef rdf fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    
    class F phase1
    class H phase2
    class N,N1,N2,N3,N4,N5,N6 reasoning
    class R,S,T,U analytics
    class V,W,X,Y,Z rdf
```

Compared to earlier - what are we noticing as a pattern?

