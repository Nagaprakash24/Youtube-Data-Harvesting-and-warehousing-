# YOUTUBE DATA HARVESTING AND WAREHOUSING USING PYTHON,MONGODB,SQL AND STREAMLIT

## INTRODUCTION
This is a Basic Project to Dive into the Data's,this Project is Dedicated to creating an user Friendly Streamlit Application,that uses the Google API Power to        Fetch the Valuable Information from Youtube,and to Collect all the Data from Youtube and to Transfer the data to MongoDB DataBase,and with the help of                 postgreSQL  Migrate the data from Mongodb to postgresql Warehouse,all within the same user friendly Streamlit Application.

## TABLE OF CONTENTS
1. Key Technologies and Skills
2. Usage
3. Features
4. Data fetching from the Youtube API
5. Storing Data in MongoDB
6. Data migration to postgreSQL Data warehouse
7. Contribution guidelines
8. Contact information

## Key Technologies and Skills
- python scripting
- API Integration
- Data Collection
- Data Management Using
  MongoDB,
  Postgresql
- Streamlit

## Usage
 Follow these steps:

  1. Install the required packages in Vs code: ```pip install -r requirement.txt``` 
  2. Run the Streamlit app in Command prompt: ```streamlit run youtubeharvesting.py```
  3. After you Run the command prompt,it will Redirect you to the following URL: ```http://localhost:8501```

## Features
  - Fetch data from the YouTube API, including channel information, playlists, videos, and comments.
  - Store the collected data in a MongoDB database.
  - Migrate the data to a postgreSQL data warehouse.
  - Analyze and visualize data using Streamlit and other Python libraries.
  - Perform queries on the MySQL data warehouse.
  - Gain insights into channel metrics, video metrics, and top 5 data of the respective channel.
  - Answer default 10 queries to provide immediate insights into the data.


## Data Retrieval from the YouTube API
  This project Uses the power of the Google API to retrieve data from YouTube channels. This data encompasses detailed information on channels, playlists, videos, and comments. By interacting with the Google API, we gather and consolidate this information into a structured format, laying the foundation for further data processing and analysis.
   
## Storing Data in MongoDB
  The Fetched data is securely stored in a MongoDB database with proper user authorization. In cases where the data already exists in the database, any subsequent attempts to insert the same data will automatically lead to data overwriting. This storage mechanism ensures efficient and updated data management and preservation, simplifying the process of handling the collected data.
  
## Data migration to postgreSQL Data warehouse
  This application empowers users to transfer data from MongoDB to a MySQL data warehouse seamlessly. Users can choose the specific channel they want to migrate from the displayed list, enabling a tailored approach to data handling.The data migration process involves transforming and structuring the collected data, ensuring it aligns with the structured format of a MySQL database.Facilitating a seamless transition of data from MongoDB to postgreSQL for further analysis and insights.
  
## Contribution Guidelines
  Contributions to this project are highly encouraged. If you come across any challenges or have ideas for enhancements, we invite you to submit a pull request. Your input is valuable to us, and we appreciate your contributions.

## Contact Information
  Email: Nagaprakash48@gmail.com
  LinkedIn: https://www.linkedin.com/in/naga-prakash-j-280aba1b9?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app
