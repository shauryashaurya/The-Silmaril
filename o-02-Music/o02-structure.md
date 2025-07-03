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
        -album_title : string                                                        
        -releaseYear : int                                                        
		%% Object Properties                                            
        +hasGenre *--1 Genre                                                        
    }                                                        
                                                        
  class RecordLabel{                                                        
		%% Data Properties                                            
        -label_name : string                                                        
        -location : string                                                        
  }                                                        
                                                        
    class Genre {                                                        
		%% Data Properties                                            
        -genre_name : string                                                        
        -description : string                                                        
    }                                                        
                                                        
  class Award{                                                        
		%% Data Properties                                            
        -award_name : string                                                        
        -year : int                                                        
        -awarding_body : string                                                        
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
   - album_title: string                                                
   - releaseYear: integer                                                
   - hasGenre -> Genre (1..*)                                                
   - // we can also keep track of songs via the inverse of featuredOn                                                
                                                
Class: RecordLabel                                                
   - label_name: string                                                
   - location: string                                                
                                                
Class: Genre                                                
   - genre_name: string                                                
   - description: string                                                
                                                
Class: Award                                                
   - award_name: string                                                
   - year: integer                                                
   - awarding_body: string                                                
```                                                 
                                                  
*(Cardinality can be adjusted. For example, an artist could be signed to multiple labels in different regions, but we’ll keep it simple.)*                                                  
                                          
---                                        
                                          
A slightly more detailed diagram. Not terribly informative, trying to render the information differently does provide more insights.    
Additionally, I wanted to put something in that could highlight `owlrl` type reasoning in a simple LR diagram.                                
                                   
                                     
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
        Award -- awarding_body_string --> awardingBody[(awardingBody)]
    end

    %% renders inline as edges between the classes
    subgraph ObjectProperties

        %% owlrl infers Song and Artist types
        Song -- performedBy --> Artist  
    
        %% owlrl infers Song and Album types
        Song -- featuredOn --> Album   
    
        %% owlrl infers Song and Genre types
        Song -- hasGenre --> Genre    
    
        %% owlrl infers Song and Award types
        Song -- hasWonAward --> Award  
    
        %% owlrl infers Artist and RecordLabel types
        Artist -- signedTo --> RecordLabel 
    
        %% owlrl infers Album and Genre types
        Album -- hasGenre --> Genre   
    
        %% Inverse of featuredOn (inferred) - owlrl will infer the inverse
        Album -- songsOnAlbum --> Song 
    end
        

    %% Inverse Properties
    %%  'songsOnAlbum' is inverse of 'featuredOn'.
    %%  'songsOnAlbum(album1, song1)' infers 'featuredOn(song1, album1)'.
    %%  'featuredOn(song2, album2)' infers 'songsOnAlbum(album2, song2)'.


    %% Functional Properties (Examples)
    %% Example: Assuming a unique song ID
    Song -- hasUniqueSongID_string --> hasUniqueSongID[(hasUniqueSongID)] 
    %% If hasUniqueSongID is functional: hasUniqueSongID(song1, "ID123") and hasUniqueSongID(song1, "ID124") is a contradiction.

    %% Example Assuming a unique Album ID
    Album -- hasUniqueAlbumID_string --> hasUniqueAlbumID[(hasUniqueAlbumID)] 

    %% Inverse Functional Properties (Examples)
    Artist -- hasUniqueArtistID_string --> hasUniqueArtistID[(hasUniqueArtistID)]
    %% If hasUniqueArtistID is inverse functional:  hasUniqueArtistID(artist1, "ID456") and hasUniqueArtistID(artist2, "ID456") infers artist1 = artist2.
      
     %% Transitive/Symmetric (consider adding based on domain needs, e.g., relatedGenre)
     %% Example Transitive:  isInfluencedBy(GenreA, GenreB) and isInfluencedBy(GenreB, GenreC) infers isInfluencedBy(GenreA, GenreC)
     %% Example Symmetric: isSimilarTo(SongA, SongB) infers isSimilarTo(SongB, SongA)
    
    %% Disjoint Classes (If we had them, e.g., Song and Artist)
    %% subgraph DisjointClasses
    %%    Song -- disjointWith --> Artist
    %% end
    %% owlrl would infer that no individual can be both a Song and an Artist

    %% Class Hierarchy (If we had subclasses, e.g., StudioAlbum and LiveAlbum)
    %% subgraph ClassHierarchy
    %%      Album <|-- StudioAlbum
    %%      Album <|-- LiveAlbum
    %%  end
    %%  owlrl would infer that any instance of StudioAlbum is also an instance of Album.                             
```                                  
                                  
                                  
  .