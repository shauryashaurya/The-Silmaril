# Draft Ontology Structure                                            
                                              
					                          
					                          
```mermaid                        
graph TD    
    subgraph Classes    
        Movie["Movie"]    
        Person["Person"]    
        Actor["Actor"]    
        Director["Director"]    
        Character_Class["Character"]    
        Genre["Genre"]    
        DisjointPersonGenre["DisjointPersonGenre"]    
    end    
    
    subgraph DataProperties    
        title["title"]    
        releaseYear["releaseYear"]    
        duration["duration"]    
        rating["rating"]    
        name["name"]    
        birthDate["birthDate"]    
        characterName["characterName"]    
        genreName["genreName"]    
        hasUniqueMovieID["hasUniqueMovieID"]    
        personHasUniqueID["personHasUniqueID"]    
    end    
    
    subgraph ObjectProperties    
        hasActor["hasActor"]    
        hasDirector["hasDirector"]    
        belongsToGenre["belongsToGenre"]    
        playsCharacter["playsCharacter"]    
        actedIn["actedIn"]    
        directed["directed"]    
        characterIn["characterIn"]    
        hasCharacter["hasCharacter"]    
    end    
        
    subgraph Individuals    
        action["action"]    
        comedy["comedy"]    
        spielberg["spielberg"]    
        hanks["hanks"]    
        forrest_gump["forrest_gump"]    
        forrest["forrest"]    
    end    
    
    Actor -- rdfs_subClassOf --> Person    
    Director -- rdfs_subClassOf --> Person    
    DisjointPersonGenre -- owl_disjointWith --> Genre    
	DisjointPersonGenre -- owl_unionOf --> Actor    
    DisjointPersonGenre -- owl_unionOf --> Director    
    
    hasActor -- rdfs_domain --> Movie    
    hasActor -- rdfs_range --> Actor    
    hasDirector -- rdfs_domain --> Movie    
    hasDirector -- rdfs_range --> Director    
    belongsToGenre -- rdfs_domain --> Movie    
    belongsToGenre -- rdfs_range --> Genre    
    playsCharacter -- rdfs_domain --> Actor    
    playsCharacter -- rdfs_range --> Character_Class    
    actedIn -- owl_inverseOf --> hasActor    
    directed -- owl_inverseOf --> hasDirector    
    characterIn -- rdfs_domain --> Character_Class    
    characterIn -- rdfs_range --> Movie    
    hasCharacter -- rdfs_domain --> Movie    
    hasCharacter -- rdfs_range --> Character_Class    
    hasCharacter --owl_inverseOf --> characterIn    
    
      
    title -- rdfs_domain --> Movie    
    title -- rdfs_range --> xsd_string    
    releaseYear -- rdfs_domain --> Movie    
    releaseYear -- rdfs_range --> xsd_integer    
    duration -- rdfs_domain --> Movie    
    duration -- rdfs_range --> xsd_integer    
    rating -- rdfs_domain --> Movie    
    rating -- rdfs_range --> xsd_float    
    name -- rdfs_domain --> Person    
    name -- rdfs_range --> xsd_string    
    birthDate -- rdfs_domain --> Person    
    birthDate -- rdfs_range --> xsd_date    
    characterName -- rdfs_domain --> Character_Class    
    characterName -- rdfs_range --> xsd_string    
    genreName -- rdfs_domain --> Genre    
    genreName --rdfs_range --> xsd_string    
    hasUniqueMovieID -- rdf_type --> owl_FunctionalProperty    
    personHasUniqueID -- rdf_type --> owl_InverseFunctionalProperty     
```                        
                            
---           
            
```mermaid                        
graph LR            
    classDef personClass fill:#f0f8ff,stroke:#a9a9a9,stroke-width:2px;              
    classDef movieClass fill:#faebd7,stroke:#a9a9a9,stroke-width:2px;              
    classDef genreClass fill:#e0ffff,stroke:#a9a9a9,stroke-width:2px;              
    classDef characterClass fill:#fff0f5,stroke:#a9a9a9,stroke-width:2px;            
            
    Movie --> hasActor --> Actor;            
    Movie --> hasDirector --> Director;            
    Movie --> belongsToGenre --> Genre;            
    Movie --> movieCharacter --> Character;            
    Actor --> playsCharacter --> Character;            
    Actor --> Person;            
    Director --> Person;            
            
    class Movie movieClass;            
    class Actor,Director,Person personClass;            
    class Genre genreClass;            
    class Character characterClass;            
            
    subgraph Legend            
        direction LR            
        Person1[Person]:::personClass            
        Movie1[Movie]:::movieClass            
        Genre1[Genre]:::genreClass            
        Character1[Character]:::characterClass            
    end                  
```                        
                            
---                        
                           
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
                                            
```pseudocode                                            
Class: Movie                                                 
   Properties (data):                                                 
      - title : string                                                 
      - releaseYear : integer                                                 
      - duration : integer                                                 
      - rating : float                                                 
   Properties (object):                                                 
      - hasActor -> Actor                                                 
      - hasDirector -> Director                                                 
      - belongsToGenre -> Genre                                                 
                                                 
Class: Person                                                 
   Properties (data):                                                 
      - name : string                                                 
      - birthDate : date                                                 
                                                 
Class: Actor (subclassOf Person)                                                 
   Properties (object):                                                 
      - playsCharacter -> Character                                                 
                                                 
Class: Director (subclassOf Person)                                                 
   (no special object property here, but reuses name/birthDate)                                                 
                                                 
Class: Character                                                 
   Properties (data):                                                 
      - name : string                                                 
                                                 
Class: Genre                                                 
   Properties (data):                                                 
      - name : string                                                 
```