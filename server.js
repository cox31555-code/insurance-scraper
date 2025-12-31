const express = require("express");
const cors = require("cors");
const path = require("path");

// Load environment variables from .env file
require('dotenv').config();

// Import the Node.js crawler module
const { main: lookupInsuranceGroup } = require('./crawler');

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, "public")));

app.get("/health", (req, res) => res.json({ ok: true }));

// Endpoint for insurance group lookup using Node.js crawler
app.post("/lookup", async (req, res) => {
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

  try {
    // Call the Node.js crawler directly
    const result = await lookupInsuranceGroup(cleanReg);
    return res.json(result);
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: "Crawler failed",
      details: error.message || String(error),
    });
  }
});

// Serve the frontend for the root route
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const port = process.env.PORT || 3001;
const host = process.env.HOST || "0.0.0.0";
app.listen(port, host, () => console.log(`API running on http://${host}:${port}`));