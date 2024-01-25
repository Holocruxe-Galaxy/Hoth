const express = require("express");
const User = require("../models/user");
const router = express.Router();
const transporter = require("../mailer");
const axios = require("axios");
const path = require("path");
const sgMail = require("../mailer");

const {spawn} = require("child_process");

const RECAPTCHA_SECRET_KEY = process.env.RECAPTCHA_SECRET_KEY;

router.post("/", async (req, res) => {
  const {name, email, captchaValue} = req.body;

  try {
    const verifyUrl = `https://www.google.com/recaptcha/api/siteverify?secret=${RECAPTCHA_SECRET_KEY}&response=${captchaValue}`;
    const response = await axios.post(verifyUrl);
    const {success} = response.data;

    if (!success) {
      return res
        .status(400)
        .json({message: "Captcha verification failed", data: response.data});
    }
  } catch (error) {
    return res.status(400).json({
      message: "Captcha verification request failed",
      error: error.toString(),
    });
  }

  //
  async function findUserByEmail(email) {
    try {
      // Realizamos la consulta find con el correo electrónico proporcionado
      const user = await User.findOne({email: email});
      return user; // Devolvemos el usuario encontrado
    } catch (error) {
      console.error(
        "Error al encontrar usuario por correo electrónico:",
        error
      );
      return null; // Devolvemos null en caso de error
    }
  }
  let alreadyUser = await findUserByEmail(email);

  if (alreadyUser) {
    const msg = {
      to: alreadyUser.email,
      from: "info@holocruxe.com",
      templateId: "d-51c4e5d7e4024b7bb3355b7111116536",
      dynamicTemplateData: {
        name: alreadyUser.name,
      },
    };

    sgMail
      .send(msg)
      .then(() => {
        console.log("Email sent");
      })
      .catch((error) => {
        console.error("Error sending email:", error);
      });
    return res.status(201).json(alreadyUser);
  } else {
    const user = new User({name, email});

    try {
      const savedUser = await user.save();
      const msg = {
        to: savedUser.email,
        from: "info@holocruxe.com",
        templateId: "d-51c4e5d7e4024b7bb3355b7111116536",
        dynamicTemplateData: {
          name: savedUser.name,
        },
      };

      sgMail
        .send(msg)
        .then(() => {
          console.log("Email sent");
        })
        .catch((error) => {
          console.error("Error sending email:", error);
        });

      res.status(201).json(savedUser);
    } catch (error) {
      res.status(400).json({message: error.message});
    }
  }
});

router.get("/startWebcam", async (req, res) => {
  try {
    const response = await axios.get("http://localhost:5000/startWebcam"); // Assuming Python service is running on port 5000
    res.json(response.data);
  } catch (err) {
    res.status(500).send("Error starting webcam");
  }
});

router.post("/runPythonScript", (req, res) => {
  const pythonScriptPath = path.join(
    __dirname,
    "../python-scripts/probando.py"
  );
  const python = spawn("python", [pythonScriptPath]);

  let scriptOutput = "";
  let errorOutput = "";

  python.stdout.on("data", (data) => {
    const output = data.toString();
    scriptOutput += output;

    // Check if our 'photo_taken' message is received
    if (output.includes("photo_taken")) {
      return res.json({status: "photo_taken"});
    }
  });

  python.stderr.on("data", (data) => {
    errorOutput += data.toString();
  });

  python.on("close", (code) => {
    if (code !== 0) {
      return res
        .status(500)
        .json({message: "Error running python script", error: errorOutput});
    }
    // For other outputs from the Python script
    return res.json({message: "Success", data: scriptOutput});
  });
});
module.exports = router;
