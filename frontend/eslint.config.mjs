import next from 'eslint-config-next';

const nextConfig = Array.isArray(next) ? next : [next];

const config = [
  {
    ignores: [
      '.next/**',
      'out/**',
      'dist/**',
      'node_modules/**',
      '.git/**',
      'public/**',
    ],
  },
  ...nextConfig,
];

export default config;
