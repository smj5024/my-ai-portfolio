export const SITE = {
  title: 'EdgeMind Lab',
  chineseTitle: '边缘智体实验室',
  description:
    '记录强化学习从数学原理、仿真实验到树莓派与 MCU 端侧部署的完整实践路径。',
  author: 'SMJ',
  github: 'https://github.com/smj5024',
  repository: 'https://github.com/smj5024/my-ai-portfolio',
} as const;

export const BASE_PATH = import.meta.env.BASE_URL.replace(/\/$/, '');

export function withBase(path = '/') {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${BASE_PATH}${normalized}`;
}

export function formatDate(date: Date) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
}

export const statusMap = {
  draft: { label: '草稿', tone: 'muted' },
  learning: { label: '学习中', tone: 'cyan' },
  planned: { label: '已规划', tone: 'amber' },
  building: { label: '制作中', tone: 'cyan' },
  validated: { label: '已验证', tone: 'green' },
  deployed: { label: '已部署', tone: 'green' },
} as const;

export type Status = keyof typeof statusMap;
