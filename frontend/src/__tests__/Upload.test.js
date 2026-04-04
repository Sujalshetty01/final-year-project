import { render, screen } from '@testing-library/react';
import Upload from '../pages/Upload';

test('renders Upload page', () => {
  render(<Upload />);
  expect(screen.getByText(/Upload/i)).toBeInTheDocument();
});
