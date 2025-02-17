# Draft Ontology Structure
  
```mermaid  
classDiagram
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
	note for Director "(no special object property for Director, but reuses name/birthDate)"

    class Character {
        -name : string
    }

    class Genre {
        -name : string
    }

    Actor --|> Person : subclassOf
    Director --|> Person : subclassOf  
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