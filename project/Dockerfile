# Base image Python 3.8
FROM python:3.8

# Packae the Techtrends application to the home directory
COPY ./techtrends /techtrends

#Expose port 3111
EXPOSE 3111

# Set work directory as /techtrends
WORKDIR /techtrends

# Install packages in requirements.txt file
RUN pip install -r requirements.txt

# Execute the init_db.py to initialize the db
RUN python init_db.py

# Start the app on container start
CMD ["python", "app.py"]