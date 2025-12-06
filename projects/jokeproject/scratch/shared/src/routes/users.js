"use strict";

const { body, validationResult } = require('express-validator');
const { getAllUsers, getUserById, createUser } = require('../db');

function routerFactory() {
  const express = require('express');
  const router = express.Router();

  // Validation middleware for createUser
  const validateUser = [
    body('name').isString().isLength({ min: 1 }).withMessage('Name is required'),
    body('email').isEmail().withMessage('Valid email is required'),
  ];

  router.get('/', async (req, res) => {
    try {
      // Basic pagination query params
      const limit = parseInt(req.query.limit, 10) || 100;
      const offset = parseInt(req.query.offset, 10) || 0;
      const users = await getAllUsers(limit, offset);
      res.json({ ok: true, users });
    } catch (err) {
      console.error('GET /users error:', err);
      res.status(500).json({ ok: false, error: 'Internal Server Error' });
    }
  });

  router.get('/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id, 10);
      if (Number.isNaN(id)) return res.status(400).json({ ok: false, error: 'Invalid id' });
      const user = await getUserById(id);
      if (!user) return res.status(404).json({ ok: false, error: 'User not found' });
      res.json({ ok: true, user });
    } catch (err) {
      console.error('GET /users/:id error:', err);
      res.status(500).json({ ok: false, error: 'Internal Server Error' });
    }
  });

  router.post('/', validateUser, async (req, res) => {
    // run validations
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ ok: false, errors: errors.array() });
    }

    try {
      const { name, email } = req.body;
      const existing = await getAllUsers(1, 0).then(list => list.find(u => u.email === email));
      if (existing) {
        return res.status(400).json({ ok: false, error: 'Email already exists' });
      }
      const user = await createUser(name, email);
      res.status(201).json({ ok: true, user });
    } catch (err) {
      console.error('POST /users error:', err);
      res.status(500).json({ ok: false, error: 'Internal Server Error' });
    }
  });

  return router;
}

module.exports = routerFactory;
