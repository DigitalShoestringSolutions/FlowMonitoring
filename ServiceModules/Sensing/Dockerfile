# ----------------------------------------------------------------------
#
#    Dockerfile script -- This file is part of the Sensing Data Collection 
#    Service Module distribution. It contains all the commands needed to 
#    assemble an image of the solution on a Raspberry Pi 4b with raspbian 
#    OS version 11 (bullseye) 32 bits. 
#
#    Copyright (C) 2022  Shoestring and University of Cambridge
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see https://www.gnu.org/licenses/.
#
# ----------------------------------------------------------------------

FROM python:3.11.2

RUN pip install --upgrade pip

# Install pip dependencies from requirements files. 
COPY ./requirements.txt /
RUN pip install -r requirements.txt
COPY ./config/requirements.txt /user_requirements.txt
RUN pip install -r user_requirements.txt

# Add both code/ and config/ to the Docker container. 
# Files inside believe they are in the same directory and can import each other freely.
WORKDIR /app
ADD ./code /app
ADD ./config /app

CMD ["python3", "/app/main.py"]
