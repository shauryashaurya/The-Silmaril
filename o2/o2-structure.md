# Ontology Structure                                    
                                      
```mermaid                                      
classDiagram                
    class Song {        
		%% Data Properties    
        -title : string                
        -duration : int                
        -releaseDate : date        
		%% Object Properties    
        +performedBy *--| Artist : many-to-one                
        +featuredOn o--| Album                
        +hasGenre *--| Genre                
        +hasWonAward *--o Award                
    }                
                
    class Artist {                
		%% Data Properties    
        -name : string                
        -birthDate : date                
        -nationality : string                
		%% Object Properties    
        +signedTo o--| RecordLabel                
    }                
                
    class Album {                
		%% Data Properties    
        -title : string                
        -releaseYear : int                
		%% Object Properties    
        +hasGenre *--| Genre                
    }                
                
  class RecordLabel{                
		%% Data Properties    
        -labelName : string                
        -location : string                
  }                
                
    class Genre {                
		%% Data Properties    
        -name : string                
        -description : string                
    }                
                
  class Award{                
		%% Data Properties    
        -awardName : string                
        -year : int                
        -awardingBody : string                
  }                
                
  class Single{                
		%% Data Properties    
		-isStandalone : boolean                
  }                
                
  class ExtendedPlay{                
		%% Data Properties    
		-numberOfTracks : int                
  }                
                
    Song *--| Artist : Association (performedBy)    
    Song o--| Album : Association (featuredOn)    
    Song *--| Genre : Association (hasGenre)    
    Song *--o Award : Association (hasWonAward)    
    Artist o--| RecordLabel : Association (signedTo)    
    Album *--| Genre : Association (hasGenre)    
    Album *--| Artist : Association (releasedBy)    
    Album *--| RecordLabel : Association (releasedBy)    
    Artist *--o Award : Association (hasWonAward)    
        
    Single --|> Song : Inheritance    
    ExtendedPlay --|> Album : Inheritance               
```                         
                                    
---          
          
```pseudocode        
Class: Song        
   - title: string        
   - duration: integer (seconds)        
   - releaseDate: date        
   - performedBy -> Artist (1..*)        
   - featuredOn -> Album (0..1)  // A song typically belongs to one album, though singles might have none        
   - hasGenre -> Genre (1..*)    // A song can fit multiple genres (e.g., Rock & Pop)        
   - hasWonAward -> Award (0..*)        
        
Class: Artist        
   - name: string        
   - birthDate: date        
   - nationality: string        
   - signedTo -> RecordLabel (0..1)  // many are unsigned/independent or signed to exactly one label        
        
Class: Album        
   - title: string        
   - releaseYear: integer        
   - hasGenre -> Genre (1..*)        
   - // we can also keep track of songs via the inverse of featuredOn        
        
Class: RecordLabel        
   - labelName: string        
   - location: string        
        
Class: Genre        
   - name: string        
   - description: string        
        
Class: Award        
   - awardName: string        
   - year: integer        
   - awardingBody: string        
```         
          
*(Cardinality can be adjusted. For example, an artist could be signed to multiple labels in different regions, but we’ll keep it simple.)*          
  