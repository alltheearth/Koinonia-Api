import { Router } from "express";
import { getContatos, postContato } from "../controllers/contatosController";

const contatosRoutes = Router();

contatosRoutes.get("/", getContatos);
contatosRoutes.post("/", postContato);

export default contatosRoutes;
