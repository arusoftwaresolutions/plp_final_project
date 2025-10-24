import express from "express";
import cors from "cors";
import helmet from "helmet";
import dotenv from "dotenv";
import { router as healthRouter } from "./routes/health.js";
import { router as usersRouter } from "./routes/users.js";
import { router as householdsRouter } from "./routes/households.js";
import { router as transactionsRouter } from "./routes/transactions.js";
import { router as aiRouter } from "./routes/ai.js";
import { router as authRouter } from "./routes/auth.js";
import swaggerUi from "swagger-ui-express";
import { openapiSpec } from "./openapi.js";
import { corsOptions } from "./security.js";

dotenv.config();

const app = express();
app.use(helmet());
app.use(cors(corsOptions));
app.use(express.json());

app.use("/api/health", healthRouter);
app.use("/api/auth", authRouter);
app.use("/api/users", usersRouter);
app.use("/api/households", householdsRouter);
app.use("/api/transactions", transactionsRouter);
app.use("/api/ai", aiRouter);

app.use("/api/docs", swaggerUi.serve, swaggerUi.setup(openapiSpec));

export default app;
