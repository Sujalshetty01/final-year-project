import { render, screen } from '@testing-library/react';
import ErrorBoundary from '../components/ErrorBoundary';
import React from 'react';

test('renders error message on error', () => {
  const ProblemChild = () => {
    throw new Error('Test error');
  };
  render(
    <ErrorBoundary>
      <ProblemChild />
    </ErrorBoundary>
  );
  expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
});
