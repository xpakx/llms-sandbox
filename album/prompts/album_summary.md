Extract and evaluate the album information. Respond in valid JSON only. 
The summary should focus on the most important features of the music and provide enough information for the user to imagine the album's strengths and weaknesses. Tags should focus on technical aspects (e.g., fingerpicking, counterpoint), musical features (e.g., female vocals, polyphonic choir), and important instruments (e.g., solo guitar, saxophone), etc.
Your response will be automatically validated and shouldn't contain any tokens outside JSON object (e.g. no '```json' part).
`probability` is the probability of the user liking the album. `summary` is an explanation of this rating. genres and tags should be list of strings
User taste: $taste
Format:  {"name": "name of album", "author": "name of author", "probability": 10, "summary": "three sentences of explanation", "genres": [], "tags": ""}
