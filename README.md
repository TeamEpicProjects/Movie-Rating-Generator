Project Name: 
Movie rating Generator


Project Description: 
The Problem we face lack of critical ratings available for movies and shows, most websites that have user's rating sometimes doesn't align with reviews. We can observe user ratings are lower for genres like comedy, horror, musical, history, art and few more less common and hybrid types. The project implements a web based solution integrated with AI component (sentiment analysis) to calculate ratings out of user reviews.


Project Duration: 
1 week


Industry: 
Entertainment


Key Contributions:
Trained and Finetuned different models to get best one for movie review dataset
Found Twitter-roBERTa-base for Sentiment Analysis best for our dataset , finetuned it tested it for movie review sentiment. (84% accuracy achieved)
Using different sentiment scores of roBERTa model , proposed a formulae to generate ratings from reviews.
created a flask based application to demonstrate the model. 
Proposed future work where task would be develop a model that will give emphasis on a specific sentiment or genre more than overall rating. Also to work with some outlier cases like sarcastic reviews.


Tech Stack:

Language: Python, 
Framework: Flask 
Frontend: Html, CSS  
Database: SQLite,  SQLAlchemy
Deep Learning / AI: HuggingFace Transformer, Numpy, Tensorflow, Keras, Matplotlib
