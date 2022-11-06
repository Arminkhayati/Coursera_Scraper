# Coursera_Scraper

**Coursera Course Data Scraper**
===============

For this project, I created a Python script that scrapes course info from coursera.org

This script has a interface where you can enter a category name corresponding to a Coursera category such as 
`Data Science <https://www.coursera.org/browse/data-science`_.

Then the script will collect all courses from this category and place them into a CSV file. Here is the info that is required from each course:

*	Course name
*	Course provider
*	Course description
*	# of Students enrolled
*	# of Ratings

The script will collect data from ALL courses within the category that is inputted. 
Once finished, the script will place the CSV file on the server and provide a link to access it.


Because of my limited knowledge of frontend development, the UI is not something pleasant. At the main page you get to select a category. Because scrapping data from courses of a category takes a long time, I made a button to download list, where you can see the status of your request. 
If it is FINNISHED then there is a download url in the json, Otherwise you have to refresh few minutes later to see if it is finneshd or not.

I haven't used any database but you could add it the project. I save data in cookie. 

For tracking status of the process of scrapper user requested, I wanted to use CELERY library but it is not stable on windows and also it uses Redis database which you cant take benefit from it on Heroku.
So I used Flask Executor which is also not stable on Heroku but it's free to use :)

It's just a hobby project. 
