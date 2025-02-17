# Draft Ontology Structure            
              
```mermaid              
%%{
    init: {
        "theme": "base",
        "themeVariables": {
            "classDiagram": {
                "fontFamily": "Arial, sans-serif"
            },
            "primaryColor": "#CFF09E",
            "nodeBorderColor": "#0B486B",
            "actorBorderColor": "#0B486B",
            "lineColor": "#0B486B"
        }
    }
}%%    

classDiagram    
    
    classDef baseClass fill:#CFF09E,stroke:#0B486B;    
    classDef subClass1 fill:#A8DBA8,stroke:#3B8686;    
    classDef subClass2 fill:#79BD9A,stroke:#3B8686;    
    classDef other1 fill:#FF6B6B,stroke:#0B486B;    
    classDef other2 fill:#C44D58,stroke:#0B486B;    
    classDef other3 fill:#C7F464,stroke:#0B486B;    
    
    
    class Movie:::other1 {    
        -title : string;    
        -releaseYear : int;    
        -duration : int;    
        -rating : float;    
        +hasActor --> Actor;    
        +hasDirector --> Director;    
        +belongsToGenre --> Genre;    
    }    
        
    class Person:::baseClass {    
        -name : string;    
        -birthDate : date;    
    }    
       
    class Actor:::subClass1 {    
        +playsCharacter --> Character;    
    }    
        
    class Director:::subClass2 {    
    }    
    note for Director "(no special object property here, but reuses name/birthDate)";    
    
    class Character:::other2 {    
        -name : string;    
    }    
        
    class Genre:::other3 {    
        -name : string;    
    }    
        
    Actor --|> Person : subclassOf;    
    Director --|> Person : subclassOf;    
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