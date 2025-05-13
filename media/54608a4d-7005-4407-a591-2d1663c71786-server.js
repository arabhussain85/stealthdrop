const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// MySQL Connection
const db = mysql.createConnection({
  host: '127.0.0.1',
  user: 'root',
  password: 'tikArab73@',
  database: 'airlinemanagementsystem'
});

db.connect(err => {
  if (err) {
    console.error('DB connection error:', err);
    return;
  }
  console.log('Connected to MySQL');
});

// Route to handle form submission
app.post('/addPassenger', (req, res) => {
    console.log('Received data:', req.body);
  const { id, firstname,lastname, email, Phone } = req.body;

  const query = 'INSERT INTO Passengers (id, firstname,lastname, email, Phone) VALUES (?, ?)';
  db.query(query, [id, firstname,lastname, email, Phone], (err, result) => {
    if (err) {
      console.error('Insert error:', err);
      res.status(500).json({ message: 'Database error' });
      return;
    }
    res.json({ message: 'Data submitted successfully!' });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

