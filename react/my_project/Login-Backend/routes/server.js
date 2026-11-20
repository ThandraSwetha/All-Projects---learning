import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth.js';
import mongoose from 'mongoose';

const app = express();
app.use(cors());
app.use(express.json)

mongoose.connect(process.env.MONGO_URI);
    .then(() => console.log('MongoDB connected'))
    .catch(err => console.log('Error in connecting MONGO DB'));

app.use('/api', authRoutes);
app.listen(5000, () => {
    console.log(' backend running on http://localhost:5000');
}
);