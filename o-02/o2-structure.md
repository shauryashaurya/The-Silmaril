# Ontology Structure                                            
                                              
```mermaid                                              
classDiagram                        
    class Song {                
		%% Data Properties            
        -title : string                        
        -duration : int                        
        -releaseDate : date                
		%% Object Properties            
        +performedBy 1--* Artist : one-to-many                        
        +featuredOn o--1 Album  : one-to-one                       
        +hasGenre 1--* Genre  : one-to-many                       
        +hasWonAward o--1 Award   : one-to-many                      
    }                        
                        
    class Artist {                        
		%% Data Properties            
        -name : string                        
        -birthDate : date                        
        -nationality : string                        
		%% Object Properties            
        +signedTo o--1 RecordLabel                        
    }                        
                        
    class Album {                        
		%% Data Properties            
        -title : string                        
        -releaseYear : int                        
		%% Object Properties            
        +hasGenre *--1 Genre                        
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
                        
    Song "1" --> "*" Artist : Association (performedBy)            
    Song "1" --> "*" Album : Association (featuredOn)            
    Song "1" --> "*" Genre : Association (hasGenre)            
    Song "1" --> "*" Award : Association (hasWonAward)            
    Artist "1" --> "1" RecordLabel : Association (signedTo)            
    Album "1" --> "*" Genre : Association (hasGenre)            
    Album "1" --> "*" Artist : Association (releasedBy)            
    Album "1" --> "1" RecordLabel : Association (releasedBy)            
    Artist "1" --> "*" Award : Association (hasWonAward)            
                
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
          
---        
            
```mermaid        
graph LR        
    subgraph Classes        
        Song["Song"]        
        Artist["Artist"]        
        Album["Album"]        
        RecordLabel["RecordLabel"]        
        Genre["Genre"]        
        Award["Award"]        
    end        
        
    subgraph DataProperties        
        Song -- title_string --> title[(title)]        
        Song -- duration_integer --> duration[(duration)]        
        Song -- releaseDate_date --> releaseDate[(releaseDate)]        
        Artist -- name_string --> name[(name)]        
        Artist -- birthDate_date --> birthDate[(birthDate)]        
        Artist -- nationality_string --> nationality[(nationality)]        
        Album -- title_string --> album_title[(title)]        
        Album -- releaseYear_integer --> releaseYear[(releaseYear)]        
        RecordLabel -- labelName_string --> labelName[(labelName)]        
        RecordLabel -- location_string --> location[(location)]        
        Genre -- name_string --> genre_name[(name)]        
        Genre -- description_string --> description[(description)]        
        Award -- awardName_string --> awardName[(awardName)]        
        Award -- year_integer --> year[(year)]        
        Award -- awardingBody_string --> awardingBody[(awardingBody)]        
    end        
        
    subgraph ObjectProperties        
      Song -- performedBy --> Artist        
      Song -- featuredOn --> Album        
      Song -- hasGenre --> Genre        
      Song -- hasWonAward --> Award        
      Artist -- signedTo --> RecordLabel        
      Album -- hasGenre --> Genre        
    end        
        
    %% Class Hierarchy (None explicit, but can be inferred if needed)        
        
    %% Disjoint Classes (None explicitly stated, consider adding if applicable)        
        
     %% Inverse Properties        
        Album -- songsOnAlbum --> Song  
		%% Inverse of featuredOn can be declared        
        
    %% Functional Properties (Examples - adjust based on actual constraints)        
      Song -- hasUniqueSongID_string --> hasUniqueSongID[(hasUniqueSongID)] 
	  %% Example: Assuming a unique song ID        
      Album -- hasUniqueAlbumID_string --> hasUniqueAlbumID[(hasUniqueAlbumID)]        
        
    %% Inverse Functional Properties (Examples - adjust based on actual constraints)        
      Artist -- hasUniqueArtistID_string --> hasUniqueArtistID[(hasUniqueArtistID)]        
              
     %% Transitive/Symmetric (consider adding based on domain needs, e.g., relatedGenre)        
        
    %% Comments explaining owlrl inferences (Examples)        
    %% rdfs:subClassOf - If a subclass relationship were present, owlrl would infer membership in the superclass.        
    %% rdfs:domain/range - owlrl uses domain and range to infer types of subjects and objects.        
    %% owl:inverseOf -  If 'songsOnAlbum' is inverse of 'featuredOn',  'songsOnAlbum(album1, song1)' infers 'featuredOn(song1, album1)'.        
    %% owl:FunctionalProperty - If 'hasUniqueSongID' is functional, owlrl ensures a song has only one ID.        
    %% owl:InverseFunctionalProperty -  'hasUniqueArtistID(artist1, id1)' and 'hasUniqueArtistID(artist2, id1)' infers artist1 = artist2.
```  
  
  
  .