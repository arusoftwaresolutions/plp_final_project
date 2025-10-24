import app from "./app.js";

const port = process.env.PORT || 10000;
app.listen(port, () => {
  console.log(`API listening on port ${port}`);
});
