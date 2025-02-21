# Draft Ontology Structure                                                    
                                                      
					                                  
					                                  
```mermaid                                
graph LR    
    subgraph Classes    
        Movie["Movie"]    
        Person["Person"]    
        Actor["Actor"]    
        Director["Director"]    
        Character_Class["Character"]    
        Genre["Genre"]    
        DisjointPersonGenre["DisjointPersonGenre"]    
    end    
    
    subgraph Data Properties    
        Movie -- title_string --> title[(title)]    
        Movie -- releaseYear_integer --> releaseYear[(releaseYear)]    
        Movie -- duration_integer --> duration[(duration)]    
        Movie -- rating_float --> rating[(rating)]    
        Person -- name_string --> name[(name)]    
        Person -- birthDate_date --> birthDate[(birthDate)]    
        Character_Class -- characterName_string --> characterName[(characterName)]    
        Genre -- genreName_string --> genreName[(genreName)]    
        Movie -- hasUniqueMovieID_string --> hasUniqueMovieID[(hasUniqueMovieID)]    
        Person -- personHasUniqueID_string --> personHasUniqueID[(personHasUniqueID)]    
    
    end    
    
    subgraph Object Properties    
        Movie -- hasActor --> Actor    
        Movie -- hasDirector --> Director    
        Movie -- belongsToGenre --> Genre    
        Actor -- playsCharacter --> Character_Class    
        Actor -- actedIn --> Movie    
        Director -- directed --> Movie    
        Character_Class -- characterIn --> Movie    
        Movie -- hasCharacter --> Character_Class    
    
    end    
    
    subgraph Individuals    
        action["action_Genre"]    
        comedy["comedy_Genre"]    
        spielberg["spielberg_Director"]    
        hanks["hanks_Actor"]    
        forrest_gump["forrest_gump_Movie"]    
        forrest["forrest_Character"]    
    end    
            
    subgraph ClassHierarchy    
      Person -- inherits --> Actor    
      Person -- inherits --> Director    
    end    
    
    subgraph Disjointness    
      DisjointPersonGenre -- disjointWith --> Genre    
      DisjointPersonGenre -- unionOf --> Actor    
      DisjointPersonGenre -- unionOf --> Director    
    end    
      
  subgraph InverseProperties    
    hasActor -- inverseOf --> actedIn    
    hasDirector -- inverseOf --> directed    
    hasCharacter -- inverseOf --> characterIn    
  end    
      
  subgraph FunctionalProperties    
    hasUniqueMovieID -- Functional --> Movie    
  end    
    
  subgraph InverseFunctionalProperties    
    personHasUniqueID -- InverseFunctional --> Person    
  end          
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