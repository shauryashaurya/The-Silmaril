# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `actors.csv`  
**Header:**  
```csv  
id,name,birthDate  
```  
**Example Data:**  
```csv  
actor_0,Mrs. Lisa Donovan,1979-09-27  
```  
---  
  
## File: `characters.csv`  
**Header:**  
```csv  
id,name  
```  
**Example Data:**  
```csv  
char_0,Kayla  
```  
---  
  
## File: `directors.csv`  
**Header:**  
```csv  
id,name,birthDate  
```  
**Example Data:**  
```csv  
director_0,Grant Kennedy,2007-09-18  
```  
---  
  
## File: `movies.csv`  
**Header:**  
```csv  
id,title,releaseYear,duration,rating,directorID,actorCharacterPairs,genres,genres_tru  
```  
**Example Data:**  
```csv  
movie_0,Movie 0 - Toy Story (1995),2014,127,8.9,director_3,"[{'actorID': 'actor_19', 'characterID': 'char_646'}, {'actorID': 'actor_63', 'characterID': 'char_523'}, {'actorID': 'actor_56', 'characterID': 'char_583'}, {'actorID': 'actor_51', 'characterID': 'char_250'}]","[{'name': 'Drama', 'description': 'Serious, narrative-driven stories'}, {'name': 'Fantasy', 'description': 'Magical and imaginative storytelling'}, {'name': 'Musical', 'description': 'Song and dance-driven narratives'}]",Adventure|Animation|Children|Comedy|Fantasy  
```  
---  
  
