import express from "express";
import cors from "cors";
import contatosRoutes from "./routes/contatos";
import historyRoutes from "./routes/history";

const app = express();

app.use(cors());
app.use(express.json());

app.use("/contatos", contatosRoutes);
app.use("/history", historyRoutes)

export default app;
