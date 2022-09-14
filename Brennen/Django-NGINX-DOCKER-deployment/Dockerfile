FROM python:3.9-alpine

# Add scripts to the path of the running container
ENV PATH="/scripts:${PATH}"

# Copy the requirements file to the docker image
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
# ^-- packacges that are required by Alpine in order to install the uWSGI(u whiskey server) to run django app in production
# RUN apk - which is the apline package command
# add - for installing a new package
# --update - update flag so that the package repositiory will be updated when we run this command
# --no-cache - specify no cache because we don't want to cache anything on the operating system because this is going to
#              a docker container and keep it lightweight as possible, doesn't store the cache when it runs the update
# --virtual .tmp - set up some virtual dependencies

# This will run the pip install command to install the dependencies in requirements.txt
RUN pip install -r /requirements.txt

# This will remove the virural setup requirements that we created after .tmp for lightweight and minimal as possible
# Best Practice: Keep your Dockerfile as light weight as possible
RUN apk del .tmp

# create a new app directory in the root of docker file
RUN mkdir /Production_Project
# copy the contents of the app to the docker file
COPY ./Production_Project /Production_Project
# means that the working directory we are going to be working from is called /app which contains Django project
WORKDIR /Production_Project
# some scripts useful for docker image
COPY ./scripts /scripts
# executable permissions to scripts in script folder and will get executable permission
RUN chmod +x /scripts/*

# create two new directories inside docker image
# -p - means create all the sub directories needed in order to get to this directory
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# This will create a new user in the image which will be used to run the application
# Best practice: when writing docker applications is to always run them as a user that has less privileges than the real user
#                if you don't do this bit then it will run the application just fine but running as the root user means
#                if your application ever gets compromised the attacker will have full room access to the container
RUN adduser -D user

# This sets the owner of these directories in line 37 and 38 so the owner of the volume directory will set to the user just created
# So the application that is running has permissions to access it
RUN chown -R user:user /vol

# 755 means that the user has full access, other groups and everyone else has just read access
# so in docker container the files will be able to read by other users but they won't be able to add or modify this files
# unless you are actually running the application as created user
RUN chmod -R 755 /vol/web

# this is where we actually switch to this new user
USER user

# this will be the entry point to the application
# it is a script that is going to be added to actually start the application
CMD ["entrypoint.sh"]
