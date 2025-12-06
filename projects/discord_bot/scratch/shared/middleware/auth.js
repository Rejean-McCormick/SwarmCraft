const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'change-me';

function authMiddleware(req, res, next) {
  // Allow health and public routes to be accessed without auth
  // Protect all /api/* routes
  // public endpoints: /api/auth (login/register) can still be protected by their own logic
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'unauthorized' });
  }
  const token = authHeader.slice(7);
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = { id: payload.id, username: payload.username };
    next();
  } catch (e) {
    res.status(401).json({ error: 'unauthorized' });
  }
}

module.exports = authMiddleware;
