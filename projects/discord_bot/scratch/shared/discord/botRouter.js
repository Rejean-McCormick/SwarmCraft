const express = require('express');
const authRouter = require('../auth/authRouter');
const walletRouter = require('../wallet/walletRouter');
const shopRouter = require('../shop/shopRouter');
const gamesRouter = require('../games/gamesRouter');

const router = express.Router();

router.use('/auth', authRouter);
router.use('/wallet', walletRouter);
router.use('/shop', shopRouter);
router.use('/games', gamesRouter);

module.exports = router;
