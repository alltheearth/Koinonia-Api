import { Request, Response } from "express";
import pool from "../db";

/**
 * GET - Lista histórico, opcionalmente filtrando por semana ou contato_id
 */
export async function getHistoricoContatos(req: Request, res: Response) {
  try {
    const { contato_id, semana_inicio } = req.query;

    let query = `SELECT 
    c.nome,
    hc.*
    FROM historico_contatos hc
    JOIN contatos c 
    ON c.id = hc.contato_id
    WHERE 1=1`;

    const values: any[] = [];

    if (contato_id) {
      values.push(contato_id);
      query += ` AND contato_id = $${values.length}`;
    }

    if (semana_inicio) {
      values.push(semana_inicio);
      query += ` AND semana_inicio = $${values.length}`;
    }

    query += " ORDER BY semana_inicio DESC";

    const result = await pool.query(query, values);
    res.json(result.rows);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Erro ao buscar histórico" });
  }
}

/**
 * POST - Cria novo registro no histórico
 */
export async function postHistoricoContato(req: Request, res: Response) {
  try {
    const {
      contato_id,
      semana_inicio,
      ultima_mensagem,
      status,
      prioridade,
      observacoes
    } = req.body;

    // Se semana_inicio não for enviado, usamos o início da semana atual
    const semana = semana_inicio
      ? new Date(semana_inicio)
      : new Date();
    semana.setDate(semana.getDate() - semana.getDay()); // segunda-feira

    const query = `
      INSERT INTO historico_contatos
        (contato_id, semana_inicio, ultima_mensagem, status, prioridade, observacoes)
      VALUES
        ($1, $2, $3, $4, $5, $6)
      RETURNING *;
    `;

    const values = [
      contato_id,
      semana.toISOString().split("T")[0],
      ultima_mensagem || null,
      status || null,
      prioridade || null,
      observacoes || null
    ];

    const result = await pool.query(query, values);
    res.status(201).json({
      message: "Histórico criado com sucesso",
      historico: result.rows[0]
    });
  } catch (error: any) {
    if (error.code === "23505") {
      return res.status(400).json({ message: "Já existe registro para esse contato nesta semana" });
    }
    console.error(error);
    res.status(500).json({ message: "Erro ao criar histórico" });
  }
}

/**
 * PUT - Atualiza dinamicamente apenas os campos enviados
 */
export async function updateHistoricoContato(req: Request, res: Response) {
  try {
    const { id } = req.params;
    const body = req.body;

    if (Object.keys(body).length === 0) {
      return res.status(400).json({ message: "Nenhum campo enviado para atualização" });
    }

    const setClauses: string[] = [];
    const values: any[] = [];

    Object.entries(body).forEach(([key, value], index) => {
      setClauses.push(`${key} = $${index + 1}`);
      values.push(value);
    });

    const query = `
      UPDATE historico_contatos
      SET ${setClauses.join(", ")}
      WHERE id = $${values.length + 1}
      RETURNING *;
    `;

    values.push(id);

    const result = await pool.query(query, values);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Histórico não encontrado" });
    }

    res.json({
      message: "Histórico atualizado com sucesso",
      historico: result.rows[0]
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Erro ao atualizar histórico" });
  }
}
