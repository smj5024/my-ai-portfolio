import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE, withBase } from '../lib/site';

export async function GET(context: { site: URL }) {
  const notes = (await getCollection('notes', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.published.valueOf() - a.data.published.valueOf(),
  );

  return rss({
    title: `${SITE.title} / ${SITE.chineseTitle}`,
    description: SITE.description,
    site: context.site,
    items: notes.map((note) => ({
      title: note.data.title,
      description: note.data.summary,
      pubDate: note.data.published,
      link: withBase(`/notes/${note.id}/`),
      categories: note.data.tags,
    })),
    customData: '<language>zh-CN</language>',
  });
}
