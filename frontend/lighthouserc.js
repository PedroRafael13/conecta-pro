module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/login',
        'http://localhost:3000/dashboard',
      ],
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',
      },
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.7 }],
        'categories:accessibility': ['error', { minScore: 0.85 }],
        'categories:best-practices': ['warn', { minScore: 0.85 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 3000 }],
        'largest-contentful-paint': ['warn', { maxNumericValue: 4000 }],
        'cumulative-layout-shift': ['warn', { maxNumericValue: 0.15 }],
        'total-blocking-time': ['warn', { maxNumericValue: 500 }],
      },
    },
    upload: {
      target: 'filesystem',
      outputDir: '../reports/lighthouse',
    },
  },
};
