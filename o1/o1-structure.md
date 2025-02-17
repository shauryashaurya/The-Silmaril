# Draft Ontology Structure                    
                      
```mermaid                      
classDiagram    
    class Movie {    
        %% Data Properties    
        -title : string    
        -releaseYear : int    
        -duration : int    
        -rating : float    
        %% Object Properties    
        +hasActor *--o Actor : many-to-one    
        +hasDirector *--o Director : many-to-one    
        +belongsToGenre *--o Genre : many-to-one    
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
	
    Movie *--o Actor : hasActor  
    Movie *--o Director : hasDirector  
    Movie *--o Genre : belongsToGenre  
    Actor --o Character : playsCharacter  
```         
                    
```UML                    
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