# Draft Ontology Structure                
                  
```mermaid                  
classDiagram    
    classDef baseClass fill:#CFF09E    
    classDef subClass1 fill:#A8DBA8    
    classDef subClass2 fill:#79BD9A    
    classDef other1 fill:#FF6B6B    
    classDef other2 fill:#C44D58    
    classDef other3 fill:#C7F464   
    
    class Movie {    
        -title : string    
        -releaseYear : int    
        -duration : int    
        -rating : float    
        +hasActor --> Actor    
        +hasDirector --> Director    
        +belongsToGenre --> Genre    
    }    
        
    class Person {    
        -name : string    
        -birthDate : date    
    }    
        
    class Actor {    
        +playsCharacter --> Character    
    }    
        
    class Director {    
    }    
    note for Director "(no special object property here, but reuses name/birthDate)"    
    
    class Character {    
        -name : string    
    }    
       
    class Genre {    
        -name : string    
    }    
        
    Actor --|> Person : subclassOf    
    Director --|> Person : subclassOf    
    
  class Movie other1    
  class Person baseClass    
  class Actor subClass1    
  class Director subClass2    
  class Character other2    
  class Genre other3      
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