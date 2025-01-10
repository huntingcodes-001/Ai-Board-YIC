const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const cors = require('cors');

const app = express();
app.use(cors());

const upload = multer({ dest: 'uploads/' });

// Ensure the recordings directory exists
const recordingsDir = path.join(__dirname, 'src', 'recordings');
if (!fs.existsSync(recordingsDir)) {
  fs.mkdirSync(recordingsDir, { recursive: true });
}

app.post('/upload', upload.single('recording'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  const filePath = path.join(recordingsDir, req.file.originalname);
  fs.rename(req.file.path, filePath, (err) => {
    if (err) {
      console.error('Error moving file:', err);
      return res.status(500).send('Error saving file.');
    }
    res.send('File uploaded and moved successfully!');
  });
});

app.listen(8000, () => {
  console.log('Server started on http://localhost:8000');
});