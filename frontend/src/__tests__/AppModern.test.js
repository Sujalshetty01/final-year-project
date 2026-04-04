import { render, screen } from '@testing-library/react';
import App from '../AppModern';

test('renders dashboard and navigation', () => {
  render(<App />);
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
});
