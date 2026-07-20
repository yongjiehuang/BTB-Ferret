

FROM node:18-alpine AS nodeapp-todo

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY ./nodejs-todo/package*.json ./

RUN npm install
# If you are building your code for production
# RUN npm ci --omit=dev

# Bundle app source
COPY ./nodejs-todo/ .

EXPOSE 3000
CMD [ "node", "index.js" ]


FROM node:18-alpine AS nodeapp-cart

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY ./nodejs-shopping-cart/package*.json ./

RUN npm install
# If you are building your code for production
# RUN npm ci --omit=dev
# 
# Bundle app source
COPY ./nodejs-shopping-cart/ .

EXPOSE 3000
CMD [ "npm", "start" ]


## The nginx reverse proxy
FROM nginx:1.25.0-alpine AS nodeapp-nginx
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
