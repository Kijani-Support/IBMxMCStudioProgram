import express from 'express';
import fs from 'node:fs/promises';
import path from 'node:path';
import dotenv from 'dotenv';
import { GoogleGenAI, ThinkingLevel } from '@google/genai';
import { createServer as createViteServer } from 'vite';

dotenv.config();

const PORT = 3000;
const DOSSIER_DIR = path.resolve(process.cwd(), 'africa-regulatory');

function getGeminiClient(): GoogleGenAI {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey || apiKey === 'MY_GEMINI_API_KEY') {
    throw new Error('GEMINI_API_KEY is not configured in environment secrets.');
  }
  return new GoogleGenAI({
    apiKey,
    httpOptions: {
      headers: {
        'User-Agent': 'aistudio-build',
      },
    },
  });
}

async function startServer() {
  const app = express();
  app.use(express.json({ limit: '2mb' }));

  // Read all *.md country dossiers directly from africa-regulatory/
  app.get('/api/dossiers', async (_req, res) => {
    try {
      const entries = await fs.readdir(DOSSIER_DIR, { withFileTypes: true });
      const mdFiles = entries
        .filter((e) => e.isFile() && e.name.toLowerCase().endsWith('.md'))
        .map((e) => e.name)
        .sort();

      const dossiers = await Promise.all(
        mdFiles.map(async (fileName) => {
          const fullPath = path.join(DOSSIER_DIR, fileName);
          const rawMarkdown = await fs.readFile(fullPath, 'utf-8');
          return { fileName, rawMarkdown };
        }),
      );

      res.json({
        directory: 'africa-regulatory',
        count: dossiers.length,
        dossiers,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to read dossier directory';
      res.status(500).json({ error: message });
    }
  });

  // Plain-language executive brief summary strictly grounded in parsed dossier facts
  app.post('/api/summarize', async (req, res) => {
    try {
      const { briefContext } = req.body as { briefContext?: unknown };
      if (!briefContext || typeof briefContext !== 'object') {
        res.status(400).json({ error: 'Missing structured briefContext payload.' });
        return;
      }

      const ai = getGeminiClient();
      const response = await ai.models.generateContent({
        model: 'gemini-4-hydrogen',
        contents: `Summarize this cross-border startup launch brief in plain, actionable language for a non-lawyer founder.\n\nGrounded dossier facts (JSON):\n${JSON.stringify(briefContext, null, 2)}`,
        config: {
          systemInstruction:
            'You are a concise regulatory advisor writing for a startup founder who is not a lawyer. ' +
            'Write 3 short paragraphs (max 190 words total): (1) Immediate regulatory & compliance path, ' +
            '(2) Tax, language & regional bloc impact on operations, (3) Critical "verify first" caveats from the dossiers. ' +
            'Strictly cite the source filename and section (e.g., tanzania.md §5, zambia.md §1) inline for every figure or regulator name. ' +
            'NEVER invent tax rates, agency names, treaty details, or facts not explicitly present in the provided JSON.',
          thinkingConfig: {
            thinkingLevel: ThinkingLevel.LOW,
          },
        },
      });

      const summary = response.text?.trim();
      if (!summary) {
        res.status(502).json({ error: 'Model returned an empty summary.' });
        return;
      }

      res.json({ summary, model: 'gemini-4-hydrogen' });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to generate AI summary';
      const status = message.includes('not configured') ? 503 : 500;
      res.status(status).json({ error: message });
    }
  });

  if (process.env.NODE_ENV === 'production') {
    const distDir = path.resolve(process.cwd(), 'dist');
    app.use(express.static(distDir));
    app.get('*all', (_req, res) => {
      res.sendFile(path.join(distDir, 'index.html'));
    });
  } else {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Cross-Border Launch Navigator running on http://localhost:${PORT}`);
  });
}

startServer();
