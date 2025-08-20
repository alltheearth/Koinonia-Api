import { Request, Response } from "express";
import pool from "../db";

export async function getContatos(req: Request, res: Response) {
  try {
    const result = await pool.query("SELECT * FROM contatos ORDER BY nome");
    res.json(result.rows);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Erro ao buscar contatos" });
  }
}

export async function postContato(req: Request, res: Response) {
  try {
    const {
      nome,
      faixa_etaria,
      classificacao,
      envolvimento,
      participacao,
      aniversario,
      rede_social,
      bairro,
      prioridade,
      ultima_mensagem,
      status,
      observacoes
    } = req.body;

    const query = `
      INSERT INTO contatos (
        nome, faixa_etaria, classificacao, envolvimento, participacao,
        aniversario, rede_social, bairro, prioridade,
        ultima_mensagem, status, observacoes
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING *;
    `;

    const values = [
      nome,
      faixa_etaria,
      classificacao,
      envolvimento,
      participacao,
      aniversario,
      rede_social,
      bairro,
      prioridade,
      ultima_mensagem,
      status,
      observacoes
    ];

    const result = await pool.query(query, values);

    res.status(201).json({
      message: "Contato criado com sucesso",
      contato: result.rows[0]
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Erro ao criar contato", error: error });
  }
}

export async function updateContato(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const body = req.body;

    // Verifica se existe algo para atualizar
    if (Object.keys(body).length === 0) {
      return res.status(400).json({ message: "Nenhum campo enviado para atualização" });
    }

    // Monta dinamicamente o SQL
    const setClauses: string[] = [];
    const values: any[] = [];

    Object.entries(body).forEach(([key, value], index) => {
      setClauses.push(`${key} = $${index + 1}`);
      values.push(value);
    });

    const query = `
      UPDATE contatos
      SET ${setClauses.join(", ")}
      WHERE id = $${values.length + 1}
      RETURNING *;
    `;

    values.push(id);

    const result = await pool.query(query, values);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Contato não encontrado" });
    }

    res.json({
      message: "Contato atualizado com sucesso",
      contato: result.rows[0]
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Erro ao atualizar contato" });
  }
}
