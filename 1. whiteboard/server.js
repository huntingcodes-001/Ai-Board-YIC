const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(express.json());

// console.log('Node.js Environment:', process.env);  // Log environment variables

const upload = multer({ dest: 'uploads/' });


const recordingsDir = path.join(__dirname, 'src', 'recordings');
if (!fs.existsSync(recordingsDir)) {
    fs.mkdirSync(recordingsDir, { recursive: true });
}

// File upload endpoint
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

// Endpoint to execute Python script
app.post('/run-python', (req, res) => {
    const scriptPath = "C:\\Users\\amirz\\Desktop\\1. Ai Board - YIC\\1. whiteboard\\src\\test_script.py";  // Update with the correct script path
    const pythonExecutable = "C:\\Python312\\python.exe"; // Replace with the full path to Python executable

    // console.log(`Running Python script: ${scriptPath} using ${pythonExecutable}`);

    const pythonProcess = spawn(pythonExecutable, [scriptPath]);

    let scriptOutput = '';
    let scriptError = '';

    pythonProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
        console.log(`Script output: ${data.toString()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        scriptError += data.toString();
        console.error(`Script error: ${data.toString()}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code: ${code}`);
        if (code === 0) {
            res.json({ message: scriptOutput.trim() });
        } else {
            res.status(500).json({
                error: `Failed to execute Python script. Exit code: ${code}`,
                stderr: scriptError.trim(),
            });
        }
    });
});


app.listen(8000, () => {
    console.log('Server started on http://localhost:8000');
});
