
from googleapiclient.discovery import build
import pandas as pd
import pymongo
import psycopg2
import streamlit as st

#Import the required python packages 

#Function for Api key
def API_CONNECT():
    #get APIKEY to access youtube data
    Api_key="AIzaSyCXU6Witdd6MvhmYtGUEAFbab0rwBKtTuE"
    Api_name="youtube"
    Api_version="v3"
    #assign all these in a variable
    youtube=build(Api_name,Api_version,developerKey=Api_key)
    return youtube
youtube=API_CONNECT()


#Function to create channel data
def get_channel_data(channel_id):
    
    #Initiating request to get channel data
    request=youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    #using the response to execute the request
    response=request.execute()
    
    #Extract the channel information,find the channel information by slicing response['items']
    for i in response['items']:
        data=dict(Channel_Name=i['snippet']['title'],
                Channel_ID=i['id'],
                Subscribers=i['statistics']['subscriberCount'],
                Views=i['statistics']['viewCount'],
                Total_Videos=i['statistics']['videoCount'],
                Channel_Description=i['snippet']['description'],
                Playlist_ID=i['contentDetails']['relatedPlaylists']['uploads'])
        
    return data
    
    
#Function to get playlist info
def get_playlist_details(channel_id):
    
    #create a variable to nextpagetoken as None
    next_page_token=None
    
    #creating an empty list to get the data
    All_data=[]
    
    #create while loop 
    while True:
        #create a request to get the playlists
        request=youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id, 
            maxResults=50,
            pageToken=next_page_token
            )
        response=request.execute()

        for item in response['items']:
                data=dict(Playlist_Id=item['id'],
                        Title=item['snippet']['title'],
                        ChannelId=item['snippet']['channelId'],
                        ChannelName=item['snippet']['channelTitle'],
                        PublishedAt=item['snippet']['publishedAt'],
                        VideoCount=item['contentDetails']['itemCount'])
                All_data.append(data)
        
        next_page_token=response.get('nextPageToken') #the nextPageToken is from response['items']
        
        #if there is no next page break the loop
        if next_page_token is None:
            break
        
    return All_data
    
    
    #Function to get video id and upload id
def get_video_id(channel_id):

    #create an empty list to get response1 sliced parameters
    video_ids=[]

    #directly creating a variable response and executing without request
    response=youtube.channels().list(id=channel_id,
        part='contentDetails').execute()

    #use the  Playlist_ID from channel data to find upload id
    Playlist_ID=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    #create a variable to get all videoid,1 page=50video id
    next_page_token=None

    #use while loop to fetch the video id 
    while True:
        response1=youtube.playlistItems().list(
            part='snippet',
            playlistId=Playlist_ID,
            maxResults=50,
            pageToken=next_page_token).execute()
        
        #use for loop to get all video ids,use len function get all data
        for i in range(len(response1['items'])):
            
            #append response to  video_ids
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
            
            #use get function,to get the data if its there
            next_page_token=response1.get('nextPageToken')
        
        #if there is no more pages break the while loop   
        if next_page_token is None:
            break
    return video_ids


#Function to get video information,
def get_video_info(video_ids):        #argument inside the function is new
    #create a empty list to get the video informtion
    video_data=[]

    #use for loop to fetch video info
    for video_id in video_ids:
        #create request to retrieve the video information
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id )
        #exeute the request by response
        response = request.execute()

        #extract the video information
        for item in response['items']:
           data = dict(Channel_Name=item['snippet']['channelTitle'],
                       channel_Id=item['snippet']['channelId'],
                       Video_ID=item['id'],
                       Title=item['snippet']['title'],
                       Tags=item['snippet'].get('tags'),
                       Thumbnail=item['snippet']['thumbnails']['default']['url'],
                       Description=item['snippet']['description'],
                       Published_Date=item['snippet']['publishedAt'],
                       Duration=item['contentDetails']['duration'],
                       Views=item['statistics']['viewCount'],
                       Likes=item['statistics'].get('likeCount'),
                       Comments=item['statistics'].get('commentCount'),
                       Favourite_count=item['statistics']['favoriteCount'],
                       Definition=item['contentDetails']['definition'],
                       Caption_status=item['contentDetails']['caption']
                       )
           video_data.append(data)
    return video_data
#the retrun function must be straight for first for loop


#Function to get comments data
def get_comment_info(video_ids):
       Comment_Information=[]
       try:
            for video_id in video_ids:
                    request=youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=50
                            )
                    response5=request.execute()

                    for item in response5["items"]:
                            comment_information=dict(
                                   Comment_Id=item['snippet']['topLevelComment']['id'],
                                   Video_Id=item['snippet']['videoId'],
                                   Comment_Text=item['snippet']['topLevelComment']['snippet']['textOriginal'],
                                   Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                   Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                            
                            Comment_Information.append(comment_information)
       except:
              pass
       
       return Comment_Information     
   
   
#transfer the data to mongodb
client=pymongo.MongoClient("mongodb://localhost:27017")
db = client["YT_DATA"]


#upload all data into mongodb
#function to add all details
def channel_details(channel_id):      
     #specific channel information   
     ch_details=get_channel_data(channel_id)
     
     #playlists for the specific channels
     pl_details=get_playlist_details(channel_id)
     
     #video ids for the specific videos
     vi_ids=get_video_id(channel_id)
     
     #get details for the specific video ids
     vi_details=get_video_info(vi_ids)
     
     #get comments details for the specific videos
     com_details=get_comment_info(vi_ids)
     
     coll1 = db["CH_DATA"]
  #now insert the data into collection1
     coll1.insert_one({"Channel_Information":ch_details,"Playlist_Information":pl_details,
                            "Video_Information":vi_details,"Comment_Information":com_details})
        
     return "Upload Completed successfully"
 
 
 

 #table creation for channels
def channels_table():
        #connect with postgresql   
    mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="PRAKASH",
                        database="DATA_OF_YOUTUBE",
                        port="5432"
                        )
    cursor = mydb.cursor()
        
    drop_query="drop table if exists channels"
    cursor.execute(drop_query)
    mydb.commit()


        #create table(query) to store data of channels

    create_query='''create table if not exists channels(Channel_Name varchar(150),
                    Channel_ID varchar(80) primary key,
                    Subscribers bigint,
                    Views bigint, 
                    Total_Videos int,
                    Channel_Description text,
                    Playlist_ID varchar(50))'''
            #execute create querys using cursor
    cursor.execute(create_query)
            #commit mydb
    mydb.commit()
    

    ch_list=[]

        #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
    #create a for loop to filter data,id:0 is we don't need id
    #i want channel information so it is :1
    #empty curly bracket is to get all channel details
    for ch_data in coll1.find({},{"_id":0,"Channel_Information":1}):
            
            #append channel inf in ch_list
        ch_list.append(ch_data["Channel_Information"])
            
            #converting the list into dataframe
    df=pd.DataFrame(ch_list)

    for index,row in df.iterrows():
                insert_query='''insert into channels(Channel_Name,
                                                            Channel_ID,
                                                            Subscribers, 
                                                            Views,
                                                            Total_Videos,
                                                            Channel_Description,
                                                            Playlist_ID)
                                                            
                                                    values(%s,%s,%s,%s,%s,%s,%s)'''
                    
                values=(
                    row['Channel_Name'],
                    row['Channel_ID'],
                    row['Subscribers'],
                    row['Views'], 
                    row['Total_Videos'],
                    row['Channel_Description'],
                    row['Playlist_ID'])
                    
                try:
                    #calling the cursor here to execute insertquery adn values
                    cursor.execute(insert_query,values)
                    mydb.commit()
                except:
                    st.write("channel table are already created")
                                      
                                      
                                      

#function to get playlist id #step5
def Playlists_table():

  #step1  
  #connect with postgresql   
    mydb=psycopg2.connect(host="localhost",
          user="postgres",
          password="PRAKASH",
          database="DATA_OF_YOUTUBE",
          port="5432"
          )
    cursor = mydb.cursor()
  
  
    drop_query="drop table if exists playlists"
    cursor.execute(drop_query)
    mydb.commit()

  #step2
  #create table(query) to store data of playlists
    try:
        create_query='''create table if not exists playlists(Playlist_Id varchar(100) primary key,
                          Title varchar(80), 
                          ChannelId varchar(100), 
                          ChannelName varchar(100),
                          PublishedAt timestamp,
                          VideoCount int)'''
      #execute create querys using cursor
        cursor.execute(create_query)
    #commit mydb
        mydb.commit()
    except:
          st.write("playlists table already created")
    
     #step3
     #create an empty list to get data        
    pl_list=[]  
    #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
           #create a for loop to filter data,id:0 is we don't need id
          #i want channel information so it is :1
            #empty curly bracket is to get all playlist details
    for pl_data in coll1.find({},{"_id":0,"Playlist_Information":1}):
    
      #use for loop to gt playlist information i is used to get the index when it is 0 i is 0,like that1,2,3....
      #to get all the playlist id use nested for
        for i in range(len(pl_data["Playlist_Information"])):
                    
          #append playlists inf in ch_list
            pl_list.append(pl_data["Playlist_Information"][i])
                    
          #converting the list into dataframe
        df1=pd.DataFrame(pl_list)
   
   #step4         
    #insert rows in tables
    #create for loop index,row and call df,iterrows is a default command to create index,row
    #iterate the data from df
    for index,row in df1.iterrows():
        insert_query = '''INSERT into playlists(Playlist_Id,
                                                  Title,
                                                  ChannelId,
                                                  ChannelName,
                                                  PublishedAt,
                                                  VideoCount)
                                      values(%s,%s,%s,%s,%s,%s)'''            
        values =(
                row['Playlist_Id'],
                row['Title'],
                row['ChannelId'],
                row['ChannelName'],
                row['PublishedAt'],
                row['VideoCount'])
              
        try:
          #calling the cursor here to execute insertquery adn values                     
            cursor.execute(insert_query,values)
            mydb.commit() 
        except:
          st.write("The playlist tables are already inserted")   
          
          

#create video for videos in postgresql
def videos_table():

  #step1  
  #connect with postgresql   
    mydb=psycopg2.connect(host="localhost",
              user="postgres",
              password="PRAKASH",
              database="DATA_OF_YOUTUBE",
              port="5432"
              )
    cursor = mydb.cursor()
  
  
    drop_query="drop table if exists videos"
    cursor.execute(drop_query)
    mydb.commit()

  #step2
  #create table(query) for videos
    try:
        create_query='''create table if not exists videos(
                  Channel_Name varchar(150),
                  channel_Id varchar(100),
                  Video_ID varchar(50) primary key,
                  Title varchar(150),
                  Tags text,
                  Thumbnail varchar(225),
                  Description text,
                  Published_Date timestamp,
                  Duration interval,
                  Views bigint,
                  Likes bigint,
                  Comments int,
                  Favourite_count int,
                  Definition varchar(10),
                  Caption_status varchar(50)
                  )'''
    
    #execute the createquery by cursor
        cursor.execute(create_query)
        mydb.commit()
    
    except:
        st.write("video Tables are already created")
    
     #step3
    #create an empty list to get data
    vi_list=[]
    #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
          #create a for loop to filter data,id:0 is we don't need id
          #i want channel information so it is :1
          #empty curly bracket is to get all video details
    for vi_data in coll1.find({},{"_id":0,"Video_Information":1}):
      
      #use for loop to gt playlist information i is used to get the index when it is 0 i is 0,like that1,2,3....
      #to get all the playlist id use nested for
        for i in range(len(vi_data["Video_Information"])):
                      
          #append playlists inf in ch_list
            vi_list.append(vi_data["Video_Information"][i])
                      
          #converting the list into dataframe
        df2=pd.DataFrame(vi_list)
          
         
    for index,row in df2.iterrows():
        insert_query = '''
                    insert into videos (Channel_Name,
                        channel_Id,
                        Video_ID,
                        Title,
                        Tags,
                        Thumbnail,
                        Description,
                        Published_Date,
                        Duration,
                        Views,
                        Likes,
                        Comments,
                        Favourite_count,
                        Definition,
                        Caption_status
                        )
                    values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''  
                
        values = (
                  row['Channel_Name'],
                  row['channel_Id'],
                  row['Video_ID'],
                  row['Title'],
                  row['Tags'],
                  row['Thumbnail'],
                  row['Description'],
                  row['Published_Date'],
                  row['Duration'],
                  row['Views'],
                  row['Likes'],
                  row['Comments'],
                  row['Favourite_count'],
                  row['Definition'],
                  row['Caption_status'])

        try:
            cursor.execute(insert_query,values)
            mydb.commit()
        except:
            st.write("The videos tables are already inserted")
    
          
          
#Function to crate comment table
def comment_tables():
    #connect with psql
    mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="PRAKASH",
                        database="DATA_OF_YOUTUBE",
                        port="5432"
                        )
    cursor=mydb.cursor()
  
   
    drop_query="drop table if exists comments"
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query='''create table if not exists comments(Comment_Id varchar(100) primary key,
                    Video_Id varchar(80),
                    Comment_Text text,
                    Comment_Author varchar(150),
                    Comment_Published timestamp)'''
        
        cursor.execute(create_query)
        mydb.commit()
        
    except:
        st.write("comment tables are already created")
        
    
      #step3
      #create an empty list to get data
    com_list=[]
      #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
              #create a for loop to filter data,id:0 is we don't need id
              #i want comment information so it is :1
              #empty curly bracket is to get all video details
    for com_data in coll1.find({},{"_id":0,"Comment_Information":1}):
          
          #use for loop to gt playlist information i is used to get the index when it is 0 i is 0,like that1,2,3....
          #to get all the playlist id use nested for
          for i in range(len(com_data["Comment_Information"])):
                          
              #append playlists inf in ch_list
            com_list.append(com_data["Comment_Information"][i])
                          
              #converting the list into dataframe
    df3=pd.DataFrame(com_list)
        
    for index,row in df3.iterrows():
            insert_query='''
                insert into comments(Comment_Id,
                                    Video_Id,
                                    Comment_Text,
                                    Comment_Author,
                                    Comment_Published )
                                    
                                    values(%s, %s, %s, %s, %s)'''
                          
            values=(
                row['Comment_Id'],
                row['Video_Id'],     
                row['Comment_Text'],   
                row['Comment_Author'],
                row['Comment_Published'])
            
            try:        
                cursor.execute(insert_query,values)
                mydb.commit()
            except:
                print("This Comments are already exists")
                        
          
            
  

#streamlit code 
#function for all tables
def tables():
    channels_table()
    Playlists_table()
    videos_table()
    comment_tables()
    
    return "Tables created successfully"


#show channel tables in streamlit
def show_channels_table():
    ch_list=[]
                #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
        #create a for loop to filter data,id:0 is we don't need id
        #i want channel information so it is :1
        #empty curly bracket is to get all channel details
    for ch_data in coll1.find({},{"_id":0,"Channel_Information":1}):
                
                #append channel inf in ch_list
        ch_list.append(ch_data["Channel_Information"])
                
        #converting the list into dataframe and to display in streamlit data frame is small letter
        #assign the st.dataframe to channels_table function
    df=st.dataframe(ch_list)
    return df
                                                  
                     
#show channel tables in streamlit
def show_playlist_table():
    
    pl_list=[]
                #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
        #create a for loop to filter data,id:0 is we don't need id
        #i want playlist information so it is :1
        #empty curly bracket is to get all playlist details
    for pl_data in coll1.find({},{"_id":0,"Playlist_Information":1}):
        #create a for loop to filter data,id:0 is we don't need id
        #i want playlist information so it is :1
        #empty curly bracket is to get all video details
        for i in range(len(pl_data["Playlist_Information"])):        
                #append channel inf in ch_list
            pl_list.append(pl_data["Playlist_Information"][i])
                
        #converting the list into dataframe and to display in streamlit data frame is small letter
        #assign the st.dataframe to playlists_table function
    df=st.dataframe(pl_list)
    return df
        
        
#show video table
def show_videos_table():
    #create an empty list to get data
    vi_list=[]
    #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
            #create a for loop to filter data,id:0 is we don't need id
            #i want video information so it is :1
            #empty curly bracket is to get all video details
    for vi_data in coll1.find({},{"_id":0,"Video_Information":1}):
        
        #use for loop to gt videos information i is used to get the index when it is 0 i is 0,like that1,2,3....
        #to get all the videos id use nested for
        for i in range(len(vi_data["Video_Information"])):
                        
            #append playlists inf in ch_list
            vi_list.append(vi_data["Video_Information"][i])
                        
            #converting the list into dataframe and to display in streamlit data frame is small letter
        #assign the st.dataframe to videos_table function
    df2=st.dataframe(vi_list)
    return df2
                             
                             
#show comment table
def show_comment_tables():
    #create an empty list to get data
    com_list=[]
        #get then data from mongodb and add in psql
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
                #create a for loop to filter data,id:0 is we don't need id
                #i want comment information so it is :1
                #empty curly bracket is to get all video details
    for com_data in coll1.find({},{"_id":0,"Comment_Information":1}):
            
            #use for loop to gt comment information i is used to get the index when it is 0 i is 0,like that1,2,3....
            #to get all the comment id use nested for
        for i in range(len(com_data["Comment_Information"])):
                            
                #append comment inf in ch_list
            com_list.append(com_data["Comment_Information"][i])
                            
                #converting the list into dataframe and to display in streamlit data frame is small letter
            #assign the st.dataframe to comments_table function
    df3=st.dataframe(com_list)
    return df3



#now writing program interface of webpage
#streamlit part
#create a sidebar for webpage
with st.sidebar:
    st.title(":blue[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("SKILLS TAKE AWAY")
    st.caption("API Integration")
    st.caption("Python scripting")
    st.caption("Data Collection")
    st.caption("MongoDB")
    st.caption("Data Management using MongoDB and SQL")
    st.caption("Streamlit")
#create letter inside the searchbar   
channel_id=st.text_input("Enter the channel id")

#create a button
if st.button("Store the Data"):
    ch_ids=[]
    db=client["YT_DATA"]
    coll1=db["CH_DATA"]
    for ch_data in coll1.find({},{"_id":0,"Channel_Information":1}):
        ch_ids.append(ch_data["Channel_Information"]["Channel_ID"])
        
    if channel_id in ch_ids:
        st.success("Channel details of the given channel id: " + channel_id + " already exists")
    else:
        insert=channel_details(channel_id)
        st.success(insert)
    
if st.button("Migrate to SQL"): 
     Table=tables()
     st.success(Table)
     
show_table=st.radio("SELECT THE TABLE FOR VIEW",("CHANNELS","PLAYLISTS","VIDEOS","COMMENTS"))

if show_table=="CHANNELS":
    show_channels_table()
    
elif show_table=="PLAYLISTS":
    show_playlist_table()
    
elif show_table=="VIDEOS":
    show_videos_table()
    
elif show_table=="COMMENTS":
    show_comment_tables()
    
    
    
#sql connection to streamlit

mydb=psycopg2.connect(host="localhost",
                    user="postgres",
                    password="PRAKASH",
                    database="DATA_OF_YOUTUBE",
                    port="5432"
                    )
cursor=mydb.cursor()
#create a variable for 10 querys,selectbox is used to select questions
question=st.selectbox(
    'Please Select Your Questions',
    ('1. All the videos and the Channel Name',
     '2. Channels with most number of views',
     '3. 10 most viewed videos',
     '4. Comments in each videos',
     '5. Videos with highest like',
     '6. likes of all videos',
     '7. views of each channel',
     '8. videos published in the year 2022',
     '9. Average duration of all videos in each channel',
     '10. Videos with highest number of comments'))



#sql connection to streamlit

mydb=psycopg2.connect(host="localhost",
                    user="postgres",
                    password="PRAKASH",
                    database="DATA_OF_YOUTUBE",
                    port="5432"
                    )
cursor=mydb.cursor()


if question=='1. All the videos and the Channel Name':
    #answer for the query1
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    #create a variable t1 to fetchall data fetchall is default
    t1=cursor.fetchall()
    df=pd.DataFrame(t1,columns=["Video Title","Channel Name"])
    st.write(df)
    
    
 
elif question=='2. Channels with most number of views':
    #write aquery
    query2='''select channel_name as channelname ,total_videos as no_videos from channels
                order by total_videos desc'''
    cursor.execute(query2)
    mydb.commit()
    #create a variable t2to fetchall data fetchall is default
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=["channel name","No of videos"])
        #add the df2 to st streamlit
    st.write(df2)
       
    
 
elif question=='3. 10 most viewed videos':
    #write aquery
    query3='''select views as views ,channel_name as channelname,title as videotitle from videos
                where views is not null order by views desc limit 10'''
    cursor.execute(query3)
    mydb.commit()
    #create a variable t3 to fetchall data fetchall is default
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=["views","channel name","videotitle"])
    #add the df3 to st streamlit
    st.write(df3)   
    

 
elif question=='4. Comments in each videos':
    #write aquery
    query4='''select comments as no_comments,title as videotitle from videos where comments is not null'''
    cursor.execute(query4)
    mydb.commit()
    #create a variable t4 to fetchall data fetchall is default
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=["no of comments","videotitle"])
    #add the df4 to st streamlit
    st.write(df4)   
        


 
elif question=='5. Videos with highest like':
    #write aquery
    query5='''select title as videotitle,channel_name as channelname,likes as likecount
                from videos where likes is not null order by likes desc'''
    cursor.execute(query5)
    mydb.commit()
    #create a variable t5 to fetchall data fetchall is default
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=["videotitle","channelname","likecount"])
    #add the df5 to st streamlit
    st.write(df5)    
    
    
 
elif question=='6. likes of all videos':
    #write aquery
    query6='''select likes as likecount,title as videotitle from videos '''
    cursor.execute(query6)
    mydb.commit()
    #create a variable t6 to fetchall data fetchall is default
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=["likecount","videotitle"])
    #add the df6 to st streamlit
    st.write(df6)     
    

 
elif question=='7. views of each channel':
    #write aquery
    query7='''select channel_name as channelname,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    #create a variable t7 to fetchall data fetchall is default
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=["likecount","videotitle"])
    #add the df7 to st streamlit
    st.write(df7)     
    
    
 
elif question=='8. videos published in the year 2022':
    #write aquery
    query8='''select title as video_title,published_date as videorelease,channel_name as channelname from videos
                where extract(year from published_date)=2022'''
    cursor.execute(query8)
    mydb.commit()
    #create a variable t8 to fetchall data fetchall is default
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=["videotitle","published_date","channelname"])
    #add the df8 to st streamlit
    st.write(df8) 
    

 
elif question=='9. Average duration of all videos in each channel':
    #write aquery
    query9='''select channel_name as channelname,AVG(duration) as averageduration from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    #create a variable t1 to fetchall data fetchall is default
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=["channelname","averageduration"])
    #create empty to append the value as a string 
    T9=[]
    for index,row in df9.iterrows():
        channel_title=row["channelname"]
        average_duration=row["averageduration"]
        average_duration_str=str(average_duration)
        T9.append(dict(channeltitle=channel_title,avgduration=average_duration_str))
    #convert the T9 into dataframe
    df1=pd.DataFrame(T9)
    st.write(df1)
    
 
elif question=='10. Videos with highest number of comments':
    #write aquery
    query10='''select title as videotitle,channel_name as channelname,comments as comments from videos where comments
                 is not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    #create a variable t1 to fetchall data fetchall is default
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=["video title","channel name","comments"])
    #add the df2 to st streamlit
    st.write(df10)  
        

