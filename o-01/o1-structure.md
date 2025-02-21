# Draft Ontology Structure                                
                                  
					              
					              
```mermaid            
graph LR    
    classDef personClass fill:#f9f,stroke:#333,stroke-width:2px;    
    classDef movieClass fill:#ccf,stroke:#333,stroke-width:2px;    
    classDef genreClass fill:#fcf,stroke:#333,stroke-width:2px;    
    
    Movie --> hasActor --> Actor;    
    Movie --> hasDirector --> Director;    
    Movie --> belongsToGenre --> Genre;    
    Movie --> movieCharacter --> Character;    
    Actor --> playsCharacter --> Character;    
    Actor --> Person;    
    Director --> Person;    
    
    class Movie movieClass;    
    class Actor personClass;    
    class Director personClass;    
    class Person personClass;    
    class Genre genreClass;    
    class Character movieClass;    
    
    subgraph Legend    
        direction LR    
        Person1[Person]:::personClass    
        Movie1[Movie]:::movieClass    
        Genre1[Genre]:::genreClass    
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