import app from "./app.js";
import { initializeDatabase } from "./services/init-db.js";

const port = process.env.PORT || 10000;

app.listen(port, async () => {
  console.log(`API listening on port ${port}`);
  
  // Initialize database tables and seed data on startup
  await initializeDatabase();
});
