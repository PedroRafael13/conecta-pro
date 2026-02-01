import '@testing-library/jest-dom';

// Mock do Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
  redirect: vi.fn(),
}));

// Mock do Next.js Image
vi.mock('next/image', () => ({
  default: (props: Record<string, unknown>) => {
    const { priority, fill, ...rest } = props;
    return Object.assign(document.createElement('img'), rest);
  },
}));
