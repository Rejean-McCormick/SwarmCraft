"use strict";

const base = '/users';

async function fetchUsers() {
  const res = await fetch(base);
  return res.json();
}

async function fetchUser(id) {
  const res = await fetch(`${base}/${id}`);
  return res.json();
}

async function createUserApi(name, email) {
  const res = await fetch(base, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email })
  });
  return res.json();
}

export { fetchUsers, fetchUser, createUserApi };
