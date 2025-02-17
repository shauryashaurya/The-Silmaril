# Draft Ontology Structure
  
```mermaid  
classDiagram
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