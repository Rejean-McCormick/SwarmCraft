"use strict";

const express = require('express');
const app = express();
app.use(express.json());

// Mount feature routers
const usersRouter = require('./infra/api/users');
if (usersRouter) {
  app.use('/api/users', usersRouter);
}

module.exports = app;
