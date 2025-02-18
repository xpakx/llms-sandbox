Extract and evaluate the album information. Respond in valid JSON only. 
Your response will be automatically validated and shouldn't contain any tokens outside JSON object (e.g. no '```json' part).
`probability` is the probability of the user liking the album. `summary` is an explanation of this rating. genres and tags should be list of strings
User taste: $taste
Format:  {"name": "name of album", "author": "name of author", "probability": 10, "summary": "one sentence of explanation", "genres": [], "tags": ""}
