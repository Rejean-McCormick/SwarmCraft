"use strict";

const express = require('express');
const app = express();
app.use(express.json());

// Mount feature routers
const usersRouter = require('./users');
if (usersRouter) {
  app.use('/api/users', usersRouter);
}

module.exports = app;
