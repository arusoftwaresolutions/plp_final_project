import { OpenAPIV3 } from "openapi-types";

export const openapiSpec: OpenAPIV3.Document = {
  openapi: "3.0.0",
  info: { title: "SDG1 API", version: "1.0.0" },
  servers: [{ url: "/" }],
  paths: {
    "/api/health": {
      get: {
        summary: "Health check",
        responses: { "200": { description: "OK" } },
      },
    },
    "/api/ai/budget/{householdId}": {
      get: {
        summary: "Get budgeting advice",
        parameters: [{ in: "path", name: "householdId", required: true, schema: { type: "integer" } }],
        responses: { "200": { description: "Advice returned" } },
      },
    },
  },
};
