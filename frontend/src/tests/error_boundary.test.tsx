import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '../components/common/ErrorBoundary';

const BrokenComponent = () => {
  throw new Error('Test crash in child component');
};

const WorkingComponent = () => <div>Normal Content Loaded</div>;

describe('ErrorBoundary Component', () => {
  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <WorkingComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText('Normal Content Loaded')).toBeInTheDocument();
  });

  it('renders recovery screen when a child component crashes', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Reload Application')).toBeInTheDocument();
    expect(screen.queryByText('Normal Content Loaded')).not.toBeInTheDocument();

    consoleSpy.mockRestore();
  });
});
