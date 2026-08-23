import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const status = z.enum(['draft', 'learning', 'planned', 'building', 'validated', 'deployed']);

const notes = defineCollection({
  loader: glob({ base: './src/content/notes', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    published: z.coerce.date(),
    updated: z.coerce.date().optional(),
    status,
    track: z.enum(['foundation', 'reinforcement-learning', 'edge-ai', 'engineering']),
    stage: z.string(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    draft: z.boolean().default(false),
  }),
});

const projects = defineCollection({
  loader: glob({ base: './src/content/projects', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    status,
    order: z.number(),
    category: z.string(),
    hardware: z.array(z.string()).default([]),
    algorithms: z.array(z.string()).default([]),
    repository: z.url().optional(),
    demo: z.string().optional(),
    started: z.coerce.date().optional(),
    updated: z.coerce.date(),
    featured: z.boolean().default(false),
    metrics: z
      .array(
        z.object({
          label: z.string(),
          value: z.string(),
        }),
      )
      .default([]),
  }),
});

const devices = defineCollection({
  loader: glob({ base: './src/content/devices', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    shortName: z.string(),
    summary: z.string(),
    status,
    order: z.number(),
    role: z.string(),
    specs: z.array(z.object({ label: z.string(), value: z.string() })),
    suitableFor: z.array(z.string()),
    constraints: z.array(z.string()),
  }),
});

export const collections = { notes, projects, devices };
