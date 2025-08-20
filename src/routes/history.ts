import { Router } from "express";
import { getContatos, postContato } from "../controllers/contatosController";
import { getHistoricoContatos, postHistoricoContato } from "../controllers/historyController";

const historyRoutes = Router();

historyRoutes.get("/", getHistoricoContatos);
historyRoutes.post("/", postHistoricoContato);

export default historyRoutes;
