const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

// Ensure the recordings directory exists
const recordingsDir = path.join(__dirname, 'src', 'recordings');
if (!fs.existsSync(recordingsDir)) {
  fs.mkdirSync(recordingsDir, { recursive: true });
}

// Endpoint to upload files
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

// Endpoint to run the Python script
app.post('/run-python', (req, res) => {
  const scriptPath = "C:\\Users\\amirz\\Desktop\\1. Ai Board - YIC\\1. whiteboard\\src\\generate_resources.py";

  // Execute the Python script
  const pythonProcess = spawn('python', [scriptPath]);

  let scriptOutput = '';
  pythonProcess.stdout.on('data', (data) => {
      scriptOutput += data.toString();
      console.log(`Script output: ${data.toString()}`); // Log script output
  });

  pythonProcess.stderr.on('data', (data) => {
      console.error(`Error from script: ${data.toString()}`); // Log errors from script
  });

  pythonProcess.on('close', (code) => {
      if (code === 0) {
          res.json({ message: scriptOutput.trim() });
      } else {
          res.status(500).send('Error executing Python script.');
      }
  });
});


app.listen(3050, () => {
  console.log('Server started on http://localhost:3050');
});
