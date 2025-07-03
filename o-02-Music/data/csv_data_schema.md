# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `albums.csv`  
**Header:**  
```csv  
id,album_title,releaseYear,genreIDs  
```  
**Example Data:**  
```csv  
album_0,Reverse-engineered human-resource paradigm Album 0,2004,"['genre_8', 'genre_10']"  
```  
---  
  
## File: `artists.csv`  
**Header:**  
```csv  
id,name,birthDate,nationality,labelID  
```  
**Example Data:**  
```csv  
artist_0,George Rivera,1997-05-15,Saint Vincent and the Grenadines,  
```  
---  
  
## File: `awards.csv`  
**Header:**  
```csv  
id,award_name,year,awarding_body  
```  
**Example Data:**  
```csv  
award_0,Grammy Award for Record of the Year,2002,British Phonographic Industry  
```  
---  
  
## File: `genres.csv`  
**Header:**  
```csv  
id,genre_name,description  
```  
**Example Data:**  
```csv  
genre_0,Funk,"Strong rhythmic groove, syncopated bass lines"  
```  
---  
  
## File: `labels.csv`  
**Header:**  
```csv  
id,label_name,location  
```  
**Example Data:**  
```csv  
label_0,"Kelly, Taylor and Fletcher",Ortizchester  
```  
---  
  
## File: `songs.csv`  
**Header:**  
```csv  
id,title,duration,releaseDate,artistIDs,albumID,genreIDs,awardIDs  
```  
**Example Data:**  
```csv  
song_0,Re-engineered analyzing benchmark Song 0,402,1983-10-03,"['artist_97', 'artist_91']",album_94,"['genre_3', 'genre_4']",[]  
```  
---  
  
