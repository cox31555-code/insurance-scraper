const express = require("express");
const cors = require("cors");
const path = require("path");
const { spawn } = require("child_process");

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, "public")));

app.get("/health", (req, res) => res.json({ ok: true }));

// New endpoint for insurance group lookup
app.post("/lookup", (req, res) => {
  const { registration } = req.body;

  if (!registration || typeof registration !== "string") {
    return res.status(400).json({ 
      success: false,
      error: "Missing 'registration' string in body" 
    });
  }

  // Clean up the registration number
  const cleanReg = registration.trim().toUpperCase().replace(/\s+/g, "");

  if (cleanReg.length < 2 || cleanReg.length > 8) {
    return res.status(400).json({
      success: false,
      error: "Invalid registration number format"
    });
  }

  const pythonBin = process.env.PYTHON_BIN || "python";
  // Pass environment variables to Python process
  const env = {
    ...process.env,
    PROXY_HOST: process.env.PROXY_HOST || "",
    PROXY_PORT: process.env.PROXY_PORT || "",
    PROXY_USER: process.env.PROXY_USER || "",
    PROXY_PASS: process.env.PROXY_PASS || ""
  };

  const py = spawn(pythonBin, ["crawler.py", cleanReg], { env });

  let out = "";
  let err = "";

  py.stdout.on("data", (d) => (out += d.toString()));
  py.stderr.on("data", (d) => (err += d.toString()));

  py.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({
        success: false,
        error: "Crawler failed",
        code,
        details: err || out,
      });
    }

    try {
      return res.json(JSON.parse(out));
    } catch {
      return res.status(500).json({
        success: false,
        error: "Crawler did not return valid JSON",
        raw: out,
        details: err,
      });
    }
  });
});

// Keep the original crawl endpoint for backward compatibility
app.post("/crawl", (req, res) => {
  const { url } = req.body;

  if (!url || typeof url !== "string") {
    return res.status(400).json({ error: "Missing 'url' string in body" });
  }

  const pythonBin = process.env.PYTHON_BIN || "python";
  const py = spawn(pythonBin, ["crawler.py", url], { env: process.env });

  let out = "";
  let err = "";

  py.stdout.on("data", (d) => (out += d.toString()));
  py.stderr.on("data", (d) => (err += d.toString()));

  py.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({
        error: "Crawler failed",
        code,
        details: err || out,
      });
    }

    try {
      return res.json(JSON.parse(out));
    } catch {
      return res.status(500).json({
        error: "Crawler did not return valid JSON",
        raw: out,
        details: err,
      });
    }
  });
});

// Serve the frontend for the root route
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const port = process.env.PORT || 3001;
app.listen(port, () => console.log(`API running on http://localhost:${port}`));
