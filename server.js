require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const usersRouter = require('./routes/users');
const morgan = require('morgan');

const app = express();

app.use(cors({
    origin: 'https://holocruxe.com',
    optionsSuccessStatus: 200
  }));
  
app.use(bodyParser.json());
app.use(morgan('dev'));

mongoose.connect(process.env.DATABASE_URL, { useNewUrlParser: true, useUnifiedTopology: true });
const db = mongoose.connection;
db.on('error', (error) => console.error(error));
db.once('open', () => console.log('Connected to Database'));

app.get('/', (req,res) => {
  res.send("<h1>Hello, world!</h1>");
});

app.use('/users', usersRouter);

app.listen(8080, () => console.log('Server is listening on port 8080'));
