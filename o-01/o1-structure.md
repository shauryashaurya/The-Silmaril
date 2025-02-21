# Draft Ontology Structure                                        
                                          
					                      
					                      
```mermaid                    
graph TD    
    subgraph "Movie Ontology"    
        Movie["Movie"]    
        Person["Person"]    
        Actor["Actor"]    
        Director["Director"]    
        Character_["Character"]    
        Genre_["Genre"]    
        ClassicMovie["ClassicMovie"]    
        Performer["Performer"]    
        NonClassicMovie["NonClassicMovie"]    
        RatingValue["RatingValue"]    
        HighlyRatedMovie["HighlyRatedMovie"]    
        MovieWithActor["MovieWithActor"]    
        MovieWithOnlyGoodActors["MovieWithOnlyGoodActors"]    
        MovieWithDirector["MovieWithDirector"]    
        GoodActor["GoodActor"]    
        Rating_G["Rating_G"]    
        Rating_PG["Rating_PG"]    
        Rating_PG13["Rating_PG13"]    
        Rating_R["Rating_R"]    
    
        Movie -- title_string --> title_string[("title : string")]    
        Movie -- releaseYear_integer --> releaseYear_integer[("releaseYear : integer")]    
        Movie -- duration_integer --> duration_integer[("duration : integer")]    
        Movie -- rating_float --> rating_float[("rating : float")]    
        Movie -- hasActor --> Actor    
        Movie -- hasDirector --> Director    
        Movie -- belongsToGenre --> Genre_    
        Movie -- isSimilarTo --> Movie    
    
        Person -- name_string --> name_string[("name : string")]    
        Person -- birthDate_date --> birthDate_date[("birthDate : date")]    
    
        Actor -- subClassOf --> Person    
        Actor -- playsCharacter --> Character_    
    
        Director -- subClassOf --> Person    
		Director -- directed --> Movie    
        Director -.-> workedOn{"workedOn"}    
    
        Character_ -- name_string2 --> name_string2[("name : string")]    
    
        Genre_ -- name_string3 --> name_string3[("name : string")]    
        Genre_ -- isInfluencedBy --> Genre_    
    
        ClassicMovie -- intersectionOf --> Movie    
        ClassicMovie -- intersectionOf --> releaseYear_lte_1980{{releaseYear <= 1980}}    
    
        Performer -- unionOf --> Actor    
        Performer -- unionOf --> Director    
    
        NonClassicMovie -- complementOf --> ClassicMovie    
    
        RatingValue -- oneOf --> Rating_G    
        RatingValue -- oneOf --> Rating_PG    
        RatingValue -- oneOf --> Rating_PG13    
        RatingValue -- oneOf --> Rating_R    
    
        HighlyRatedMovie -- intersectionOfH --> Movie    
        HighlyRatedMovie -- intersectionOfH --> rating_is_5{{rating = 5.0}}    
    
        MovieWithActor -- intersectionOfMA --> Movie    
        MovieWithActor -- intersectionOfMA --> hasActor_someValuesFrom{{hasActor someValuesFrom Actor}}    
    
        MovieWithOnlyGoodActors -- intersectionOfMOGA --> Movie    
        MovieWithOnlyGoodActors -- intersectionOfMOGA--> hasActor_allValuesFrom{{hasActor allValuesFrom GoodActor}}    
        GoodActor -- subClassOfGA --> Actor    
    
		MovieWithDirector -- intersectionOfMWD --> Movie    
		MovieWithDirector -- intersectionOfMWD --> hasDirector_cardinality_1{{hasDirector cardinality 1}}    
        name_string3 -- equivalentProperty --> personName_string[("personName : string")]    
    end    
    Movie -.-> actedIn{"actedIn"}    
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