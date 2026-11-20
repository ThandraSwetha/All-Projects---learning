// backend file for authentication

import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import User from '../models/User.js';
import {authenticateToken } from '../middleware/authMiddleware.js';

const router = express.Router();
